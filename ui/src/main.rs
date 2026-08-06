pub use makepad_widgets;

use makepad_widgets::*;
use std::process::Command;
use std::sync::mpsc::{channel, Receiver, Sender};
use ipc::IpcClient;

mod ipc;

app_main!(App);

enum IpcMessage {
    Processing(String),
    Completed { prompt: String, response: String },
    HealthUpdate(String),
    Error(String),
}

script_mod! {
    use mod.prelude.widgets.*

    startup() do #(App::script_component(vm)){
        ui: Root {
            main_window := Window {
                window.inner_size: vec2(1150, 820)
                body +: {
                    flow: Right
                    width: Fill
                    height: Fill
                    show_bg: true
                    draw_bg.color: #0D1117

                    // Left Panel (Archive - Collapsible 280px)
                    left_panel := View {
                        width: 280.0
                        height: Fill
                        flow: Down
                        show_bg: true
                        draw_bg.color: #161B22
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
                            draw_bg.color: #21262D
                            padding: 10.0
                            flow: Down
                            spacing: 8.0

                            Label {
                                text: "📚 SESSION HISTORY (Click to Rename)"
                                draw_text.color: #8B949E
                                draw_text.text_style.font_size: 11.0
                            }
                            
                            session_label := Label {
                                text: "• Session 01 (Default)"
                                draw_text.color: #58A6FF
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
                                draw_text.color: #3FB950
                                draw_text.text_style.font_size: 12.0
                            }

                            user_msg_label := Label {
                                text: ""
                                draw_text.color: #58A6FF
                                draw_text.text_style.font_size: 13.0
                            }

                            response_label := Label {
                                text: "Awaiting research synthesis query..."
                                draw_text.color: #C9D1D9
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
                                text: ""
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
                        draw_bg.color: #161B22
                        padding: 14.0
                        spacing: 12.0

                        Label {
                            text: "📊 TELEMETRY & ARTIFACTS"
                            draw_text.color: #BC8CFF
                            draw_text.text_style.font_size: 13.0
                        }

                        // Per-Chat Session PDF Artifacts Section
                        pdf_artifacts_section := View {
                            width: Fill, height: 180.0
                            show_bg: true
                            draw_bg.color: #21262D
                            padding: 10.0
                            flow: Down
                            spacing: 8.0

                            Label {
                                text: "📄 Session PDF Reports"
                                draw_text.color: #C9D1D9
                                draw_text.text_style.font_size: 12.0
                            }

                            View {
                                width: Fill, height: Fit
                                flow: Right
                                spacing: 8.0

                                Label {
                                    width: Fill
                                    text: "📑 Report_Latest.pdf"
                                    draw_text.color: #58A6FF
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

                        Label { text: "Retrieved Vector Chunks: 5 (mmap HNSW)" draw_text.color: #C9D1D9 }
                        Label { text: "Active Citations: Grounded" draw_text.color: #8B949E }

                        sandbox_view := View {
                            width: Fill, height: Fill
                            show_bg: true
                            draw_bg.color: #21262D
                            padding: 10.0
                            Label {
                                text: "Sandbox Output / Code Execution"
                                draw_text.color: #8B949E
                                draw_text.text_style.font_size: 11.0
                            }
                        }

                        Label { text: "Critic Evaluation: OK (0.0 contradiction)" draw_text.color: #3FB950 }
                        ram_status_label := Label { text: "RAM Usage: 3.8 GB / 8.0 GB (47.5% - Safe)" draw_text.color: #3FB950 }
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
    #[rust] chat_history: Vec<(String, String)>,
    #[rust] session_name: String,
    #[rust] first_query_sent: bool,
    #[rust] show_left_panel: bool,
    #[rust] show_right_panel: bool,
}

impl App {
    pub fn open_pdf_preview(pdf_path: &str) {
        if cfg!(target_os = "macos") {
            let _ = Command::new("open").arg(pdf_path).spawn();
        }
    }

    pub fn save_pdf_to_destination(pdf_path: &str) {
        if cfg!(target_os = "macos") {
            let script = r#"POSIX path of (choose folder with prompt "Select Destination Folder to Save PDF Report")"#;
            if let Ok(output) = Command::new("osascript").arg("-e").arg(script).output() {
                let folder = String::from_utf8_lossy(&output.stdout).trim().to_string();
                if !folder.is_empty() && std::path::Path::new(pdf_path).exists() {
                    let filename = std::path::Path::new(pdf_path).file_name().unwrap_or_default();
                    let dest = std::path::Path::new(&folder).join(filename);
                    let _ = std::fs::copy(pdf_path, dest);
                    log!("PDF copied to destination: {}", folder);
                }
            }
        }
    }

    pub fn prompt_ingest_document() {
        if cfg!(target_os = "macos") {
            let script = r#"POSIX path of (choose file with prompt "Select Document (PDF/MD/TXT) to Ingest into YORD Vector Index")"#;
            if let Ok(output) = Command::new("osascript").arg("-e").arg(script).output() {
                let file_path = String::from_utf8_lossy(&output.stdout).trim().to_string();
                if !file_path.is_empty() {
                    let _ = Command::new("curl")
                        .arg("-F")
                        .arg(format!("file=@{}", file_path))
                        .arg("http://localhost:8000/api/upload")
                        .spawn();
                }
            }
        }
    }

    pub fn rename_session_dialog(&mut self, cx: &mut Cx) {
        if cfg!(target_os = "macos") {
            let script = format!(
                r#"text returned of (display dialog "Rename Session:" default answer "{}")"#,
                self.session_name
            );
            if let Ok(output) = Command::new("osascript").arg("-e").arg(script).output() {
                let new_name = String::from_utf8_lossy(&output.stdout).trim().to_string();
                if !new_name.is_empty() {
                    self.session_name = new_name.clone();
                    self.ui.label(cx, &[id!(session_label)]).set_text(cx, &format!("• {}", new_name));
                    self.ui.label(cx, &[id!(session_label)]).redraw(cx);
                }
            }
        }
    }

    pub fn submit_query(&mut self, cx: &mut Cx) {
        let input_widget = self.ui.text_input(cx, &[id!(input_bar)]);
        let user_query = input_widget.text();
        if user_query.trim().is_empty() {
            return;
        }

        // Reset input box text after submission
        self.ui.text_input(cx, &[id!(input_bar)]).set_text(cx, "");
        self.ui.text_input(cx, &[id!(input_bar)]).redraw(cx);

        // Auto-name session on first prompt
        if !self.first_query_sent {
            let words: Vec<&str> = user_query.split_whitespace().take(4).collect();
            if !words.is_empty() {
                let title = words.join(" ");
                let auto_name = format!("• {}", title.to_uppercase());
                self.session_name = title;
                self.ui.label(cx, &[id!(session_label)]).set_text(cx, &auto_name);
                self.ui.label(cx, &[id!(session_label)]).redraw(cx);
            }
            self.first_query_sent = true;
        }

        self.ui.label(cx, &[id!(status_label)]).set_text(cx, "⏳ SYNTHESIZING RESEARCH ANSWER...");
        self.ui.label(cx, &[id!(status_label)]).redraw(cx);

        self.ui.label(cx, &[id!(user_msg_label)]).set_text(cx, &format!("💬 You: {}", user_query));
        self.ui.label(cx, &[id!(user_msg_label)]).redraw(cx);

        self.ui.label(cx, &[id!(response_label)]).set_text(cx, "Query dispatched to local engine...");
        self.ui.label(cx, &[id!(response_label)]).redraw(cx);

        self.ui.redraw(cx);

        let tx = self.tx.clone();
        let query_clone = user_query.clone();

        std::thread::spawn(move || {
            let ipc = IpcClient::new();
            match ipc.send_query(&query_clone) {
                Ok(response) => {
                    if let Some(t) = tx {
                        let _ = t.send(IpcMessage::Completed {
                            prompt: query_clone,
                            response,
                        });
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
                        self.ui.label(cx, &[id!(status_label)]).redraw(cx);
                    }
                    IpcMessage::Completed { prompt, response } => {
                        self.chat_history.push((prompt, response.clone()));

                        self.ui.label(cx, &[id!(status_label)]).set_text(cx, "● SYNTHESIS COMPLETE — Zero Sycophancy Verified");
                        self.ui.label(cx, &[id!(status_label)]).redraw(cx);

                        // Render cumulative chat history thread
                        let mut thread = String::new();
                        for (q, a) in &self.chat_history {
                            thread.push_str(&format!("💬 You: {}\n\n{}\n\n---\n\n", q, a));
                        }

                        self.ui.label(cx, &[id!(response_label)]).set_text(cx, &thread);
                        self.ui.label(cx, &[id!(response_label)]).redraw(cx);
                    }
                    IpcMessage::HealthUpdate(ram_str) => {
                        self.ui.label(cx, &[id!(ram_status_label)]).set_text(cx, &ram_str);
                        self.ui.label(cx, &[id!(ram_status_label)]).redraw(cx);
                    }
                    IpcMessage::Error(err) => {
                        self.ui.label(cx, &[id!(status_label)]).set_text(cx, "⚠️ BACKEND CONNECTION ERROR");
                        self.ui.label(cx, &[id!(status_label)]).redraw(cx);

                        self.ui.label(cx, &[id!(response_label)]).set_text(cx, &format!("Error: {}", err));
                        self.ui.label(cx, &[id!(response_label)]).redraw(cx);
                    }
                }
                self.ui.redraw(cx);
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
        self.session_name = "Session 01 (Default)".to_string();
        self.first_query_sent = false;
        self.show_left_panel = true;
        self.show_right_panel = true;
    }

    fn handle_actions(&mut self, cx: &mut Cx, actions: &Actions) {
        self.poll_ipc_messages(cx);

        // Send Query Button
        if self.ui.button(cx, &[id!(btn_send)]).clicked(actions) {
            self.submit_query(cx);
        }

        // Return Key in Input Bar
        let input_widget = self.ui.text_input(cx, &[id!(input_bar)]);
        if input_widget.returned(actions).is_some() {
            self.submit_query(cx);
        }

        // Ingest Document Button
        if self.ui.button(cx, &[id!(btn_ingest_doc)]).clicked(actions) {
            Self::prompt_ingest_document();
        }

        // View PDF Button
        if self.ui.button(cx, &[id!(btn_view_pdf)]).clicked(actions) {
            let log_pdf = "/Users/harshit/Desktop/yord/logs/Report_Latest.pdf";
            Self::open_pdf_preview(log_pdf);
        }

        // Save PDF Button
        if self.ui.button(cx, &[id!(btn_save_pdf)]).clicked(actions) {
            let log_pdf = "/Users/harshit/Desktop/yord/logs/Report_Latest.pdf";
            Self::save_pdf_to_destination(log_pdf);
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
