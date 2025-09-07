const ytdl = require('ytdl-core');

module.exports = async (req, res) => {
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // OPTIONS 요청 처리
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  try {
    const { videoId } = req.query;
    
    if (!videoId) {
      return res.status(400).json({ error: 'videoId가 필요합니다' });
    }
    
    const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
    
    // 비디오 정보 가져오기
    const info = await ytdl.getInfo(videoUrl);
    
    // 자막 찾기
    const captions = info.player_response?.captions?.playerCaptionsTracklistRenderer?.captionTracks;
    
    if (!captions || captions.length === 0) {
      return res.json({ subtitle: '자막 없음' });
    }
    
    // 한국어 자막 우선 찾기
    let selectedCaption = captions.find(caption => 
      caption.languageCode === 'ko' || caption.languageCode === 'ko-KR'
    );
    
    // 한국어 없으면 첫 번째 자막 사용
    if (!selectedCaption) {
      selectedCaption = captions[0];
    }
    
    // 자막 URL에서 내용 가져오기
    const subtitleUrl = selectedCaption.baseUrl;
    const response = await fetch(subtitleUrl);
    const subtitleXml = await response.text();
    
    // XML에서 텍스트만 추출
    const textMatches = subtitleXml.match(/<text[^>]*>(.*?)<\/text>/g);
    if (!textMatches) {
      return res.json({ subtitle: '자막 파싱 실패' });
    }
    
    const subtitleText = textMatches
      .map(match => match.replace(/<[^>]*>/g, ''))
      .join(' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .trim();
    
    return res.json({ subtitle: subtitleText || '자막 없음' });
    
  } catch (error) {
    console.error('자막 수집 오류:', error);
    return res.status(500).json({ 
      error: '자막 수집 실패', 
      message: error.message 
    });
  }
};
