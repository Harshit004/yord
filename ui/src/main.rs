pub use makepad_widgets;

use makepad_widgets::*;
use std::process::Command;

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

                    // Left Panel (Archive - Collapsible 280px)
                    left_panel := View {
                        width: 280.0
                        height: Fill
                        flow: Down
                        show_bg: true
                        draw_bg.color: #1A1A1A
                        padding: 12.0
                        spacing: 12.0

                        View {
                            width: Fill, height: Fit
                            flow: Right
                            align: {y: 0.5}

                            Label {
                                text: "Archive & History"
                                draw_text.color: #00A8FF
                                draw_text.text_style.font_size: 14.0
                            }
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
                    }

                    // Center Panel (Synthesis & Chat - Fluid)
                    center_panel := View {
                        width: Fill
                        height: Fill
                        flow: Down
                        padding: 12.0
                        spacing: 12.0

                        // Header Bar with Toggle Buttons
                        header_bar := View {
                            width: Fill, height: Fit
                            flow: Right
                            align: {y: 0.5}
                            spacing: 12.0

                            btn_toggle_left := Button {
                                text: "◧ Toggle Archive"
                            }

                            Label {
                                width: Fill
                                text: "YORD AI Harness — Cognitive Synthesis"
                                draw_text.color: #E0E0E0
                                draw_text.text_style.font_size: 16.0
                            }

                            btn_toggle_right := Button {
                                text: "Toggle Telemetry & Artifacts ◨"
                            }
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
                            text: "Ask YORD to analyze papers, solve math, or process queries..."
                        }
                    }

                    // Right Panel (Transparency & Artifacts - Collapsible 320px)
                    right_panel := View {
                        width: 320.0
                        height: Fill
                        flow: Down
                        show_bg: true
                        draw_bg.color: #1A1A1A
                        padding: 12.0
                        spacing: 12.0

                        Label {
                            text: "Telemetry & Artifacts"
                            draw_text.color: #00A8FF
                            draw_text.text_style.font_size: 14.0
                        }

                        // Per-Chat Session PDF Artifacts Section
                        pdf_artifacts_section := View {
                            width: Fill, height: 180.0
                            show_bg: true
                            draw_bg.color: #141414
                            padding: 8.0
                            flow: Down
                            spacing: 6.0

                            Label {
                                text: "📄 Session PDF Reports"
                                draw_text.color: #E0E0E0
                                draw_text.text_style.font_size: 12.0
                            }

                            View {
                                width: Fill, height: Fit
                                flow: Right
                                spacing: 8.0

                                Label {
                                    width: Fill
                                    text: "📑 Report_Latest.pdf"
                                    draw_text.color: #00A8FF
                                    draw_text.text_style.font_size: 11.0
                                }
                                btn_view_pdf := Button {
                                    text: "👁️ View"
                                }
                                btn_save_pdf := Button {
                                    text: "📥 Save"
                                }
                            }
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

impl App {
    pub fn open_pdf_preview(pdf_path: &str) {
        if cfg!(target_os = "macos") {
            let _ = Command::new("open").arg(pdf_path).spawn();
        }
    }
}

impl MatchEvent for App {
    fn handle_startup(&mut self, _cx: &mut Cx) {
        log!("YORD UI main window loaded with PDF Artifact Manager.");
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
