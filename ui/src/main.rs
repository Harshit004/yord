pub use makepad_widgets;

use makepad_widgets::*;

mod ipc;

app_main!(App);

script_mod! {
    use mod.prelude.widgets.*

    startup() do #(App::script_component(vm)){
        ui: Root {
            main_window := Window {
                window.inner_size: vec2(1024, 768)
                body +: {
                    flow: Right
                    width: Fill
                    height: Fill

                    // Left Panel (Archive)
                    left_panel := View {
                        width: 280.0
                        height: Fill
                        flow: Down
                        show_bg: true
                        draw_bg.color: #1A1A1A
                        padding: 12.0
                        spacing: 12.0

                        Label {
                            text: "Archive & History"
                            draw_text.color: #00A8FF
                            draw_text.text_style.font_size: 14.0
                        }
                        View {
                            width: Fill, height: Fill
                            show_bg: true
                            draw_bg.color: #141414
                            padding: 8.0
                            Label {
                                text: "File Explorer / Session History"
                                draw_text.color: #888888
                                draw_text.text_style.font_size: 12.0
                            }
                        }
                        Button {
                            text: "Export PDF Report"
                        }
                    }

                    // Center Panel (Synthesis & Chat)
                    center_panel := View {
                        width: Fill
                        height: Fill
                        flow: Down
                        padding: 12.0
                        spacing: 12.0

                        Label {
                            text: "YORD AI Harness — Cognitive Synthesis"
                            draw_text.color: #E0E0E0
                            draw_text.text_style.font_size: 16.0
                        }

                        chat_view := View {
                            width: Fill
                            height: Fill
                            show_bg: true
                            draw_bg.color: #141414
                            padding: 12.0
                            flow: Down
                            spacing: 8.0
                            
                            Label {
                                text: "System Ready. Enter a research request below..."
                                draw_text.color: #00E676
                                draw_text.text_style.font_size: 12.0
                            }
                        }
                        
                        input_bar := TextInput {
                            width: Fill
                            height: Fit
                            text: "Ask YORD to analyze papers, solve math, or draft marketing..."
                        }
                    }

                    // Right Panel (Transparency & Metrics)
                    right_panel := View {
                        width: 320.0
                        height: Fill
                        flow: Down
                        show_bg: true
                        draw_bg.color: #1A1A1A
                        padding: 12.0
                        spacing: 12.0

                        Label {
                            text: "Transparency & Guardian"
                            draw_text.color: #00A8FF
                            draw_text.text_style.font_size: 14.0
                        }

                        Label { text: "Retrieved Vector Chunks: 0" draw_text.color: #E0E0E0 }
                        Label { text: "Active Citations: None" draw_text.color: #888888 }

                        sandbox_view := View {
                            width: Fill, height: Fill
                            show_bg: true
                            draw_bg.color: #141414
                            padding: 8.0
                            Label {
                                text: "Sandbox Output / Code Execution"
                                draw_text.color: #888888
                                draw_text.text_style.font_size: 11.0
                            }
                        }

                        Label { text: "Critic Evaluation: OK (0.0 contradiction)" draw_text.color: #00E676 }
                        Label { text: "Memory Guardian: < 150MB RAM (Normal)" draw_text.color: #888888 }
                    }
                }
            }
        }
    }
}

#[derive(Script, ScriptHook)]
pub struct App {
    #[live] ui: WidgetRef,
}

impl MatchEvent for App {
    fn handle_startup(&mut self, _cx: &mut Cx) {
        log!("YORD UI main window loaded.");
    }
}

impl AppMain for App {
    fn script_mod(vm: &mut ScriptVm) -> ScriptValue {
        crate::makepad_widgets::script_mod(vm);
        self::script_mod(vm)
    }

    fn handle_event(&mut self, cx: &mut Cx, event: &Event) {
        self.match_event(cx, event);
        self.ui.handle_event(cx, event, &mut Scope::empty());
    }
}
