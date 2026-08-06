use std::collections::HashMap;

#[allow(dead_code)]
pub struct IpcClient {
    pub base_url: String,
    pub ws_url: String,
}

#[allow(dead_code)]
impl IpcClient {
    pub fn new() -> Self {
        Self {
            base_url: "http://localhost:8000".to_string(),
            ws_url: "ws://localhost:8000/ws/stream".to_string(),
        }
    }

    pub fn health_url(&self) -> String {
        format!("{}/health", self.base_url)
    }

    pub fn query_url(&self) -> String {
        format!("{}/api/query", self.base_url)
    }

    pub fn send_query(&self, query_text: &str) -> Result<String, String> {
        let mut map = HashMap::new();
        map.insert("query", query_text);
        map.insert("session_id", "default_session");

        match ureq::post(&self.query_url())
            .send_json(map) {
                Ok(resp) => {
                    if let Ok(json) = resp.into_json::<serde_json::Value>() {
                        if let Some(text) = json.get("synthesized_text").and_then(|v| v.as_str()) {
                            return Ok(text.to_string());
                        }
                    }
                    Ok("Response received from YORD backend.".to_string())
                }
                Err(e) => Err(format!("Backend error: {}", e))
            }
    }
}
