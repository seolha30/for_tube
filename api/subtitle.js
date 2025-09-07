module.exports = async (req, res) => {
  // CORS 헤더
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // 일단 테스트용 응답
  const { videoId } = req.query;
  
  if (!videoId) {
    return res.json({ error: 'videoId가 필요합니다' });
  }
  
  // YouTube Data API v3 방식으로 변경 예정
  return res.json({ 
    success: true,
    videoId: videoId,
    message: '자막 API 테스트 성공!',
    subtitle: '테스트 자막 내용입니다.'
  });
};
