pub use makepad_widgets;

use makepad_widgets::*;
use std::process::Command;
use ipc::IpcClient;

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
                                width: Fill
                                text: "Archive & History"
                                draw_text.color: #00A8FF
                                draw_text.text_style.font_size: 14.0
                            }
                        }

                        btn_ingest_doc := Button {
                            width: Fill
                            text: "📁 + Ingest Document (PDF/MD)"
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
                            
                            status_label := Label {
                                text: "System Ready. Enter a research request below..."
                                draw_text.color: #00E676
                                draw_text.text_style.font_size: 12.0
                            }
                            
                            response_label := Label {
                                text: "Awaiting input query..."
                                draw_text.color: #CCCCCC
                                draw_text.text_style.font_size: 13.0
                            }
                        }
                        
                        input_container := View {
                            width: Fill, height: Fit
                            flow: Right
                            spacing: 8.0

                            input_bar := TextInput {
                                width: Fill
                                height: Fit
                                text: "Hi who are you?"
                            }

                            btn_send := Button {
                                text: "Send ➔"
                            }
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
                        ram_status_label := Label { text: "RAM Usage: 3.8 GB / 8.0 GB (47.5% - Safe)" draw_text.color: #00E676 }
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

    pub fn handle_query_submission(&mut self, cx: &mut Cx) {
        let input_widget = self.ui.text_input(cx, &[id!(input_bar)]);
        let user_query = input_widget.text();

        if !user_query.trim().is_empty() {
            log!("Submitting query to YORD backend: {}", user_query);
            self.ui.label(cx, &[id!(status_label)]).set_text(cx, &format!("Processing: '{}'...", user_query));

            let ipc = IpcClient::new();
            match ipc.send_query(&user_query) {
                Ok(synthesized_output) => {
                    self.ui.label(cx, &[id!(status_label)]).set_text(cx, "Synthesis Complete");
                    self.ui.label(cx, &[id!(response_label)]).set_text(cx, &synthesized_output);
                }
                Err(err) => {
                    self.ui.label(cx, &[id!(status_label)]).set_text(cx, "Error Querying Backend");
                    self.ui.label(cx, &[id!(response_label)]).set_text(cx, &format!("Backend connection error: {}", err));
                }
            }
        }
    }
}

impl MatchEvent for App {
    fn handle_startup(&mut self, _cx: &mut Cx) {
        log!("YORD UI main window loaded with active submission handlers.");
    }

    fn handle_actions(&mut self, cx: &mut Cx, actions: &Actions) {
        if self.ui.button(cx, &[id!(btn_send)]).clicked(actions) {
            self.handle_query_submission(cx);
        }

        let input_widget = self.ui.text_input(cx, &[id!(input_bar)]);
        if input_widget.returned(actions).is_some() {
            self.handle_query_submission(cx);
        }

        if self.ui.button(cx, &[id!(btn_view_pdf)]).clicked(actions) {
            let log_pdf = "/Users/harshit/Desktop/yord/logs/Report_Latest.pdf";
            Self::open_pdf_preview(log_pdf);
        }
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
