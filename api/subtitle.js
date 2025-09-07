module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  const { videoId } = req.query;
  
  res.json({
    success: true,
    message: "API 테스트 성공!",
    videoId: videoId || "없음",
    timestamp: new Date().toISOString()
  });
};
