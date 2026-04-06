import { useEffect, useCallback } from 'react';

export function useMultimodalTTS(modalityPlan) {
  const playTTS = useCallback(() => {
    if (!modalityPlan || !modalityPlan.tts_text) return;
    
    window.speechSynthesis.cancel(); 
    const msg = new SpeechSynthesisUtterance(modalityPlan.tts_text);
    msg.rate = modalityPlan.tts_speed || 0.85; 
    
    const voices = window.speechSynthesis.getVoices();
    // Prefer Google US or natural english voices if available
    msg.voice = voices.find(v => v.name.includes("Google US English")) || voices.find(v => v.lang.includes("en-US")) || voices[0];
    
    window.speechSynthesis.speak(msg);
  }, [modalityPlan]);

  // Auto-play on mount if preferred
  useEffect(() => {
    if (modalityPlan && (modalityPlan.primary_modality === 'audio' || modalityPlan.stimulus_format.includes('audio'))) {
      playTTS();
    }
    return () => window.speechSynthesis.cancel();
  }, [modalityPlan, playTTS]);

  return { playTTS };
}
