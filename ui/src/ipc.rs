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
}
