import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../api';
import type { TTSProvider } from '../types';

export function useTTS(
  initialEnabled = true,
  initialProvider: TTSProvider = 'browser',
  elevenlabsAvailable = false,
) {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [provider, setProviderState] = useState<TTSProvider>(
    initialProvider === 'elevenlabs' && elevenlabsAvailable ? 'elevenlabs' : 'browser',
  );
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsWarning, setTtsWarning] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const browserSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;
  const supported = browserSupported || elevenlabsAvailable;

  const stopAudioElement = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
      audioRef.current = null;
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    stopAudioElement();
    if (browserSupported) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  }, [browserSupported, stopAudioElement]);

  const setProvider = useCallback(
    (next: TTSProvider) => {
      if (next === 'elevenlabs' && !elevenlabsAvailable) return;
      stop();
      setTtsWarning(null);
      setProviderState(next);
    },
    [elevenlabsAvailable, stop],
  );

  const speakBrowser = useCallback(
    (text: string) => {
      if (!browserSupported) return;
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.03;
      utterance.pitch = 1.0;

      const voices = window.speechSynthesis.getVoices();
      const preferred =
        voices.find(
          (v) =>
            /en-(GB|US)/i.test(v.lang) && /Samantha|Daniel|Google UK|Natural/i.test(v.name),
        ) || voices.find((v) => /en/i.test(v.lang));
      if (preferred) {
        utterance.voice = preferred;
      }

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    },
    [browserSupported],
  );

  const speak = useCallback(
    (text: string, force = false) => {
      if (!supported) return;
      if (!enabled && !force) return;

      stop();
      setTtsWarning(null);

      if (provider === 'elevenlabs' && elevenlabsAvailable) {
        const controller = new AbortController();
        abortRef.current = controller;
        setIsSpeaking(true);

        api
          .synthesizeSpeech(text, controller.signal)
          .then((blob) => {
            if (controller.signal.aborted) return;
            const url = URL.createObjectURL(blob);
            audioUrlRef.current = url;
            const audio = new Audio(url);
            audioRef.current = audio;
            audio.onended = () => {
              stopAudioElement();
              setIsSpeaking(false);
            };
            audio.onerror = () => {
              stopAudioElement();
              setIsSpeaking(false);
            };
            return audio.play();
          })
          .catch((err) => {
            if (controller.signal.aborted) return;
            stopAudioElement();
            setIsSpeaking(false);
            const msg = err instanceof Error ? err.message : 'ElevenLabs playback failed';
            setTtsWarning(`ElevenLabs unavailable (${msg}); fell back to browser voice.`);
            speakBrowser(text);
          });
        return;
      }

      speakBrowser(text);
    },
    [elevenlabsAvailable, enabled, provider, speakBrowser, stop, stopAudioElement, supported],
  );

  useEffect(() => {
    if (!enabled) {
      stop();
    }
  }, [enabled, stop]);

  useEffect(() => {
    return () => stop();
  }, [stop]);

  return {
    enabled,
    setEnabled,
    provider,
    setProvider,
    isSpeaking,
    supported,
    ttsWarning,
    speak,
    stop,
  };
}
