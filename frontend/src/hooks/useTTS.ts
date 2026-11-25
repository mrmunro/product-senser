import { useCallback, useEffect, useState } from 'react';

export function useTTS(initialEnabled = true) {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  const stop = useCallback(() => {
    if (!supported) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, [supported]);

  const speak = useCallback(
    (text: string, force = false) => {
      if (!supported) return;
      if (!enabled && !force) return;
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.03;
      utterance.pitch = 1.0;

      const voices = window.speechSynthesis.getVoices();
      const preferred =
        voices.find((v) => /en-(GB|US)/i.test(v.lang) && /Samantha|Daniel|Google UK|Natural/i.test(v.name)) ||
        voices.find((v) => /en/i.test(v.lang));
      if (preferred) {
        utterance.voice = preferred;
      }

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    },
    [enabled, supported],
  );

  useEffect(() => {
    if (!enabled) {
      stop();
    }
  }, [enabled, stop]);

  useEffect(() => {
    return () => stop();
  }, [stop]);

  return { enabled, setEnabled, isSpeaking, supported, speak, stop };
}
