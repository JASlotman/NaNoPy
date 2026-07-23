import importlib
import os
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from sdl2 import SDL_WasInit


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

canvas_module = importlib.import_module("NaNoPy.classes.canvas")
mainloop_module = importlib.import_module("NaNoPy.classes.mainloop")

CanvasNaive = canvas_module.CanvasNaive
Mainloop = mainloop_module.Mainloop


class MainloopInitializationTests(unittest.TestCase):
    def test_construction_is_lazy_and_has_no_process_side_effects(self):
        with patch.object(mainloop_module, "SDL_InitSubSystem") as initialize:
            loop = Mainloop()

        self.assertFalse(loop.running)
        self.assertFalse(loop._sdl_initialized)
        initialize.assert_not_called()

    def test_initialization_failure_contains_sdl_diagnostic(self):
        loop = Mainloop()
        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=-1),
            patch.object(mainloop_module, "SDL_GetError", return_value=b"video unavailable"),
        ):
            with self.assertRaisesRegex(RuntimeError, "video unavailable"):
                loop.ensure_initialized()

        self.assertFalse(loop.running)
        self.assertFalse(loop._sdl_initialized)

    def test_stop_clears_resources_and_allows_reuse(self):
        canvas = SimpleNamespace(
            _persistent_texture=object(),
            renderer=object(),
            window=object(),
        )

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0) as initialize,
            patch.object(mainloop_module, "SDL_QuitSubSystem") as quit_subsystem,
            patch.object(mainloop_module, "SDL_DestroyTexture") as destroy_texture,
            patch.object(mainloop_module, "SDL_DestroyRenderer") as destroy_renderer,
            patch.object(mainloop_module, "SDL_DestroyWindow") as destroy_window,
        ):
            loop = Mainloop()
            loop.ensure_initialized()
            self.assertTrue(loop.running)

            loop.canvasses["canvas"] = canvas
            loop.listeners["listener"] = object()
            loop.multiple_windows = True
            loop.stop()

            self.assertFalse(loop.running)
            self.assertEqual(loop.canvasses, {})
            self.assertEqual(loop.listeners, {})
            self.assertFalse(loop.multiple_windows)
            destroy_texture.assert_called_once()
            destroy_renderer.assert_called_once()
            destroy_window.assert_called_once()

            # A stopped global mainloop is deliberately reusable.
            loop.ensure_initialized()
            self.assertTrue(loop.running)
            loop.stop()

        self.assertEqual(initialize.call_count, 2)
        self.assertEqual(quit_subsystem.call_count, 2)

    def test_independent_mainloops_hold_balanced_sdl_references(self):
        initial_state = SDL_WasInit(mainloop_module.SDL_INIT_VIDEO)
        first = Mainloop()
        second = Mainloop()

        try:
            first.ensure_initialized()
            second.ensure_initialized()
            self.assertTrue(SDL_WasInit(mainloop_module.SDL_INIT_VIDEO))

            first.stop()
            self.assertTrue(second.running)
            self.assertTrue(SDL_WasInit(mainloop_module.SDL_INIT_VIDEO))

            second.stop()
            self.assertEqual(
                SDL_WasInit(mainloop_module.SDL_INIT_VIDEO),
                initial_state,
            )
        finally:
            if first._sdl_initialized:
                first.stop()
            if second._sdl_initialized:
                second.stop()

    def test_cross_thread_stop_is_rejected_without_tearing_down_sdl(self):
        loop = Mainloop()
        errors = []

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem") as quit_subsystem,
        ):
            loop.ensure_initialized()

            worker = threading.Thread(
                target=lambda: self._capture_exception(loop.stop, errors)
            )
            worker.start()
            worker.join()

            self.assertEqual(len(errors), 1)
            self.assertRegex(str(errors[0]), "thread that created")
            self.assertTrue(loop.running)
            self.assertTrue(loop._sdl_initialized)
            quit_subsystem.assert_not_called()

            loop.stop()

        quit_subsystem.assert_called_once_with(mainloop_module.SDL_INIT_VIDEO)

    @staticmethod
    def _capture_exception(func, errors):
        try:
            func()
        except Exception as exc:
            errors.append(exc)

    def test_listener_can_stop_without_mutating_active_iteration(self):
        loop = Mainloop()
        first_listener = MagicMock()
        second_listener = MagicMock()
        first_listener.run.side_effect = lambda _event: loop.stop()
        loop.listeners = {
            "first": first_listener,
            "second": second_listener,
        }

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem"),
            patch.object(mainloop_module, "SDL_PollEvent", side_effect=[1, 0]),
        ):
            loop.ensure_initialized()
            self.assertFalse(loop._handle_events())

        first_listener.run.assert_called_once()
        second_listener.run.assert_not_called()

    def test_embedded_close_returns_quietly_without_reading_destroyed_renderer(self):
        loop = Mainloop()
        canvas = SimpleNamespace(
            name="closing",
            window=object(),
            renderer=object(),
            _persistent_texture=object(),
            _reload_fonts=False,
            _window_size_cache=(2, 2),
            get_window_size=lambda: (2, 2),
        )

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem"),
            patch.object(mainloop_module, "SDL_DestroyTexture"),
            patch.object(mainloop_module, "SDL_DestroyRenderer"),
            patch.object(mainloop_module, "SDL_DestroyWindow"),
            patch.object(mainloop_module, "SDL_RenderReadPixels") as read_pixels,
            patch.object(mainloop_module, "SDL_RenderClear") as clear_renderer,
        ):
            loop.ensure_initialized()
            loop.canvasses[canvas.name] = canvas

            def close_during_events():
                loop.stop()
                return False

            with patch.object(loop, "_handle_events", side_effect=close_during_events):
                image = loop.update_embedded(canvas)

            self.assertEqual(image.size, (2, 2))
            self.assertEqual(image.getpixel((0, 0)), (0, 0, 0, 255))
            self.assertFalse(loop.clear(canvas))

        read_pixels.assert_not_called()
        clear_renderer.assert_not_called()

    def test_update_then_clear_is_quiet_when_close_arrives_during_update(self):
        """Regression test for the animation-loop shutdown traceback."""

        loop = Mainloop()
        canvas = SimpleNamespace(
            name="closing",
            window=object(),
            renderer=object(),
            _persistent_texture=None,
            _reload_fonts=False,
        )

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem"),
            patch.object(mainloop_module, "SDL_GetWindowFlags", return_value=0),
            patch.object(mainloop_module, "SDL_RenderPresent"),
            patch.object(mainloop_module, "SDL_DestroyRenderer"),
            patch.object(mainloop_module, "SDL_DestroyWindow"),
            patch.object(mainloop_module, "SDL_RenderClear") as clear_renderer,
        ):
            loop.ensure_initialized()
            loop.canvasses[canvas.name] = canvas

            def close_during_update():
                loop.stop()
                return False

            with patch.object(loop, "_handle_events", side_effect=close_during_update):
                self.assertFalse(loop.update(canvas))

            # This is the exact operation that follows update() in the demos
            # from the reported traceback. It must not touch the destroyed
            # renderer or turn a normal window close into an exception.
            self.assertFalse(loop.clear(canvas))

        clear_renderer.assert_not_called()

    def test_foreign_window_event_is_requeued_for_its_own_mainloop(self):
        loop = Mainloop()
        canvas = SimpleNamespace(
            name="owned",
            window=object(),
            renderer=object(),
            _persistent_texture=None,
            _reload_fonts=False,
            _window_size_cache=(2, 2),
        )

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem"),
            patch.object(mainloop_module, "SDL_GetWindowID", return_value=10),
            patch.object(mainloop_module, "SDL_GetWindowFromID", return_value=object()),
            patch.object(mainloop_module, "SDL_PushEvent", return_value=1) as push_event,
            patch.object(mainloop_module, "SDL_PollEvent", side_effect=[1, 0]),
            patch.object(mainloop_module, "SDL_DestroyRenderer"),
            patch.object(mainloop_module, "SDL_DestroyWindow"),
        ):
            loop.ensure_initialized()
            loop.canvasses[canvas.name] = canvas
            loop.event.type = mainloop_module.SDL_WINDOWEVENT
            loop.event.window.event = mainloop_module.SDL_WINDOWEVENT_CLOSE
            loop.event.window.windowID = 20

            self.assertTrue(loop._handle_events())
            self.assertTrue(loop.running)
            push_event.assert_called_once()
            loop.stop()

    def test_foreign_keyboard_event_is_not_delivered_to_this_loops_listeners(self):
        loop = Mainloop()
        listener = MagicMock()
        canvas = SimpleNamespace(
            name="owned",
            window=object(),
            renderer=object(),
            _persistent_texture=None,
        )

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem"),
            patch.object(mainloop_module, "SDL_GetWindowID", return_value=10),
            patch.object(mainloop_module, "SDL_GetWindowFromID", return_value=object()),
            patch.object(mainloop_module, "SDL_PushEvent", return_value=1) as push_event,
            patch.object(mainloop_module, "SDL_PollEvent", side_effect=[1, 0]),
            patch.object(mainloop_module, "SDL_DestroyRenderer"),
            patch.object(mainloop_module, "SDL_DestroyWindow"),
        ):
            loop.ensure_initialized()
            loop.canvasses[canvas.name] = canvas
            loop.listeners["listener"] = listener
            loop.event.type = mainloop_module.SDL_KEYDOWN
            loop.event.key.windowID = 20

            self.assertTrue(loop._handle_events())
            listener.run.assert_not_called()
            push_event.assert_called_once()
            loop.stop()

    def test_duplicate_canvas_name_cannot_replace_the_registered_canvas(self):
        loop = Mainloop()
        original = SimpleNamespace(name="duplicate")
        loop.canvasses[original.name] = original

        with self.assertRaisesRegex(ValueError, "must be unique"):
            loop.add_canvas(SimpleNamespace(name="duplicate"))

        self.assertIs(loop.canvasses[original.name], original)
        self.assertFalse(loop._sdl_initialized)

    def test_keep_uses_the_window_aware_event_dispatcher(self):
        loop = Mainloop()
        dispatch_results = iter((True, False))

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem"),
            patch.object(loop, "_handle_events", side_effect=dispatch_results) as dispatch,
            patch.object(mainloop_module, "SDL_Delay") as delay,
        ):
            loop.ensure_initialized()
            loop.keep()
            loop.stop()

        self.assertEqual(dispatch.call_count, 2)
        delay.assert_called_once_with(10)


class CanvasResourceTests(unittest.TestCase):
    def make_loop(self):
        loop = MagicMock()
        loop._sdl_error.return_value = "mock SDL failure"
        return loop

    def test_duplicate_name_is_rejected_before_any_sdl_allocation(self):
        loop = self.make_loop()
        loop._require_canvas_name_available.side_effect = ValueError(
            "Canvas names must be unique"
        )

        with patch.object(canvas_module, "SDL_CreateWindow") as create_window:
            with self.assertRaisesRegex(ValueError, "must be unique"):
                CanvasNaive("duplicate", 20, 10, NNP=loop)

        create_window.assert_not_called()
        loop.ensure_initialized.assert_not_called()
        loop._destroy_canvas_resources.assert_not_called()

    def test_window_creation_failure_raises_and_does_not_register_canvas(self):
        loop = self.make_loop()
        with patch.object(canvas_module, "SDL_CreateWindow", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "mock SDL failure"):
                CanvasNaive("broken", 20, 10, NNP=loop)

        loop.add_canvas.assert_not_called()
        loop._destroy_canvas_resources.assert_called_once()
        loop.release_if_unused.assert_called_once()

    def test_default_renderer_falls_back_to_target_capable_software(self):
        loop = self.make_loop()
        window = object()
        renderer = object()

        with (
            patch.object(canvas_module, "SDL_CreateWindow", return_value=window),
            patch.object(
                canvas_module,
                "SDL_CreateRenderer",
                side_effect=[None, renderer],
            ) as create_renderer,
        ):
            canvas = CanvasNaive("headless", 20, 10, NNP=loop)

        self.assertIs(canvas.renderer, renderer)
        self.assertEqual(
            create_renderer.call_args_list,
            [
                call(window, -1, canvas_module.RENDER_FLAGS),
                call(
                    window,
                    -1,
                    canvas_module.SDL_RENDERER_SOFTWARE
                    | canvas_module.SDL_RENDERER_TARGETTEXTURE,
                ),
            ],
        )
        loop.ensure_persistent_texture.assert_called_once_with(canvas)
        loop.add_canvas.assert_called_once_with(canvas)

    def test_explicit_renderer_failure_does_not_silently_fallback(self):
        loop = self.make_loop()
        with (
            patch.object(canvas_module, "SDL_CreateWindow", return_value=object()),
            patch.object(canvas_module, "SDL_CreateRenderer", return_value=None) as create_renderer,
        ):
            with self.assertRaisesRegex(RuntimeError, "mock SDL failure"):
                CanvasNaive("broken renderer", 20, 10, driver=3, NNP=loop)

        create_renderer.assert_called_once()
        loop.add_canvas.assert_not_called()
        loop._destroy_canvas_resources.assert_called_once()

    def test_texture_creation_failure_is_fatal(self):
        loop = Mainloop()
        canvas = SimpleNamespace(
            name="textureless",
            window=object(),
            renderer=object(),
            _persistent_texture=None,
            get_window_size=lambda: (20, 10),
        )

        with (
            patch.object(mainloop_module, "SDL_InitSubSystem", return_value=0),
            patch.object(mainloop_module, "SDL_QuitSubSystem"),
            patch.object(mainloop_module, "SDL_CreateTexture", return_value=None),
            patch.object(mainloop_module, "SDL_GetError", return_value=b"no target textures"),
        ):
            loop.ensure_initialized()
            try:
                with self.assertRaisesRegex(RuntimeError, "no target textures"):
                    loop.ensure_persistent_texture(canvas)
            finally:
                loop.stop()


if __name__ == "__main__":
    unittest.main()
