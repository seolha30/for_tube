export default function handler(req, res) {
  return res.json({ 
    message: "API 작동중!",
    path: req.url,
    method: req.method,
    query: req.query
  });
}
