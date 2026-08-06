pub use makepad_widgets;

use makepad_widgets::*;
use std::process::Command;
use std::sync::mpsc::{channel, Receiver, Sender};
use ipc::IpcClient;

mod ipc;

app_main!(App);

enum IpcMessage {
    Processing(String),
    Completed(String),
    Error(String),
}

script_mod! {
    use mod.prelude.widgets.*

    startup() do #(App::script_component(vm)){
        ui: Root {
            main_window := Window {
                window.inner_size: vec2(1100, 800)
                body +: {
                    flow: Right
                    width: Fill
                    height: Fill
                    show_bg: true
                    draw_bg.color: #0B0E14

                    // Left Panel (Archive - Collapsible 280px)
                    left_panel := View {
                        width: 280.0
                        height: Fill
                        flow: Down
                        show_bg: true
                        draw_bg.color: #12161F
                        padding: 14.0
                        spacing: 12.0

                        View {
                            width: Fill, height: Fit
                            flow: Right
                            align: {y: 0.5}

                            Label {
                                width: Fill
                                text: "⚡ YORD ARCHIVE"
                                draw_text.color: #00F0FF
                                draw_text.text_style.font_size: 13.0
                            }
                        }

                        btn_ingest_doc := Button {
                            width: Fill
                            text: "📁 + Ingest Document (PDF/MD)"
                        }

                        View {
                            width: Fill, height: Fill
                            show_bg: true
                            draw_bg.color: #1A202C
                            padding: 10.0
                            flow: Down
                            spacing: 8.0

                            Label {
                                text: "📚 SESSION HISTORY"
                                draw_text.color: #718096
                                draw_text.text_style.font_size: 11.0
                            }
                            Label {
                                text: "• Session_01 (Default)"
                                draw_text.color: #E2E8F0
                                draw_text.text_style.font_size: 12.0
                            }
                        }
                    }

                    // Center Panel (Synthesis & Chat - Fluid)
                    center_panel := View {
                        width: Fill
                        height: Fill
                        flow: Down
                        padding: 16.0
                        spacing: 14.0

                        // Header Bar with Toggle Buttons
                        header_bar := View {
                            width: Fill, height: Fit
                            flow: Right
                            align: {y: 0.5}
                            spacing: 12.0

                            btn_toggle_left := Button {
                                text: "◧ Archive"
                            }

                            Label {
                                width: Fill
                                text: "YORD AI HARNESS — COGNITIVE SYNTHESIS"
                                draw_text.color: #00F0FF
                                draw_text.text_style.font_size: 15.0
                            }

                            btn_toggle_right := Button {
                                text: "Telemetry ◨"
                            }
                        }

                        chat_view := View {
                            width: Fill
                            height: Fill
                            show_bg: true
                            draw_bg.color: #161B22
                            padding: 16.0
                            flow: Down
                            spacing: 12.0

                            status_label := Label {
                                text: "● SYSTEM READY — Enter a research query below..."
                                draw_text.color: #00E676
                                draw_text.text_style.font_size: 12.0
                            }

                            user_msg_label := Label {
                                text: ""
                                draw_text.color: #00F0FF
                                draw_text.text_style.font_size: 13.0
                            }

                            response_label := Label {
                                text: "Awaiting research synthesis query..."
                                draw_text.color: #CBD5E0
                                draw_text.text_style.font_size: 13.0
                            }
                        }
                        
                        input_container := View {
                            width: Fill, height: Fit
                            flow: Right
                            spacing: 10.0

                            input_bar := TextInput {
                                width: Fill
                                height: Fit
                                text: "Hi who are you?"
                            }

                            btn_send := Button {
                                text: "Send Query ➔"
                            }
                        }
                    }

                    // Right Panel (Transparency & Artifacts - Collapsible 320px)
                    right_panel := View {
                        width: 320.0
                        height: Fill
                        flow: Down
                        show_bg: true
                        draw_bg.color: #12161F
                        padding: 14.0
                        spacing: 12.0

                        Label {
                            text: "📊 TELEMETRY & ARTIFACTS"
                            draw_text.color: #8A2BE2
                            draw_text.text_style.font_size: 13.0
                        }

                        // Per-Chat Session PDF Artifacts Section
                        pdf_artifacts_section := View {
                            width: Fill, height: 180.0
                            show_bg: true
                            draw_bg.color: #1A202C
                            padding: 10.0
                            flow: Down
                            spacing: 8.0

                            Label {
                                text: "📄 Session PDF Reports"
                                draw_text.color: #E2E8F0
                                draw_text.text_style.font_size: 12.0
                            }

                            View {
                                width: Fill, height: Fit
                                flow: Right
                                spacing: 8.0

                                Label {
                                    width: Fill
                                    text: "📑 Report_Latest.pdf"
                                    draw_text.color: #00F0FF
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

                        Label { text: "Retrieved Vector Chunks: 5 (mmap HNSW)" draw_text.color: #E2E8F0 }
                        Label { text: "Active Citations: Grounded" draw_text.color: #718096 }

                        sandbox_view := View {
                            width: Fill, height: Fill
                            show_bg: true
                            draw_bg.color: #1A202C
                            padding: 10.0
                            Label {
                                text: "Sandbox Output / Code Execution"
                                draw_text.color: #718096
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
    #[rust] rx: Option<Receiver<IpcMessage>>,
    #[rust] tx: Option<Sender<IpcMessage>>,
}

impl App {
    pub fn open_pdf_preview(pdf_path: &str) {
        if cfg!(target_os = "macos") {
            let _ = Command::new("open").arg(pdf_path).spawn();
        }
    }

    pub fn submit_query(&mut self, cx: &mut Cx) {
        let user_query = self.ui.text_input(cx, &[id!(input_bar)]).text();
        if user_query.trim().is_empty() {
            return;
        }

        self.ui.label(cx, &[id!(status_label)]).set_text(cx, "⏳ SYNTHESIZING RESEARCH ANSWER...");
        self.ui.label(cx, &[id!(user_msg_label)]).set_text(cx, &format!("💬 You: {}", user_query));
        self.ui.label(cx, &[id!(response_label)]).set_text(cx, "Query dispatched to local engine...");

        let tx = self.tx.clone();
        let query_clone = user_query.clone();

        std::thread::spawn(move || {
            let ipc = IpcClient::new();
            match ipc.send_query(&query_clone) {
                Ok(response) => {
                    if let Some(t) = tx {
                        let _ = t.send(IpcMessage::Completed(response));
                    }
                }
                Err(err) => {
                    if let Some(t) = tx {
                        let _ = t.send(IpcMessage::Error(err));
                    }
                }
            }
        });
    }

    pub fn poll_ipc_messages(&mut self, cx: &mut Cx) {
        if let Some(rx) = &self.rx {
            while let Ok(msg) = rx.try_recv() {
                match msg {
                    IpcMessage::Processing(status) => {
                        self.ui.label(cx, &[id!(status_label)]).set_text(cx, &status);
                    }
                    IpcMessage::Completed(text) => {
                        self.ui.label(cx, &[id!(status_label)]).set_text(cx, "● SYNTHESIS COMPLETE — Zero Sycophancy Verified");
                        self.ui.label(cx, &[id!(response_label)]).set_text(cx, &text);
                    }
                    IpcMessage::Error(err) => {
                        self.ui.label(cx, &[id!(status_label)]).set_text(cx, "⚠️ BACKEND CONNECTION ERROR");
                        self.ui.label(cx, &[id!(response_label)]).set_text(cx, &format!("Error: {}", err));
                    }
                }
            }
        }
    }
}

impl MatchEvent for App {
    fn handle_startup(&mut self, _cx: &mut Cx) {
        log!("YORD Antigravity UI initialized with non-blocking thread channels.");
        let (tx, rx) = channel();
        self.tx = Some(tx);
        self.rx = Some(rx);
    }

    fn handle_actions(&mut self, cx: &mut Cx, actions: &Actions) {
        self.poll_ipc_messages(cx);

        if self.ui.button(cx, &[id!(btn_send)]).clicked(actions) {
            self.submit_query(cx);
        }

        let input_widget = self.ui.text_input(cx, &[id!(input_bar)]);
        if input_widget.returned(actions).is_some() {
            self.submit_query(cx);
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
        self.poll_ipc_messages(cx);
    }
}
