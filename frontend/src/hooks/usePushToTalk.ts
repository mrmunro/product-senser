import { useCallback, useEffect, useRef, useState } from 'react';

export type TurnLengthStatus = 'normal' | 'amber' | 'red';

interface UsePushToTalkOptions {
  disabled: boolean;
  onRecordingComplete: (blob: Blob, durationSeconds: number) => void;
  onRecordingStart?: () => void;
}

export function usePushToTalk({
  disabled,
  onRecordingComplete,
  onRecordingStart,
}: UsePushToTalkOptions) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [micError, setMicError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const startedAtRef = useRef<number>(0);
  const timerRef = useRef<number | null>(null);
  const spaceHeldRef = useRef(false);

  const stopTracks = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, []);

  const clearTimer = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const startRecording = useCallback(async () => {
    if (disabled || isRecording) return;
    setMicError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : '';

      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        clearTimer();
        const durationSec = Math.max(0.5, (Date.now() - startedAtRef.current) / 1000);
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || 'audio/webm',
        });
        stopTracks();
        setIsRecording(false);
        setRecordingSeconds(0);
        if (blob.size > 0) {
          onRecordingComplete(blob, durationSec);
        }
      };

      mediaRecorderRef.current = recorder;
      startedAtRef.current = Date.now();
      recorder.start(250);
      setIsRecording(true);
      setRecordingSeconds(0);
      onRecordingStart?.();

      timerRef.current = window.setInterval(() => {
        setRecordingSeconds(Math.floor((Date.now() - startedAtRef.current) / 1000));
      }, 250);
    } catch (err) {
      stopTracks();
      const message =
        err instanceof Error
          ? err.message
          : 'Microphone access was denied. Enable mic permissions in Chrome and try again.';
      setMicError(message);
    }
  }, [clearTimer, disabled, isRecording, onRecordingComplete, onRecordingStart, stopTracks]);

  const stopRecording = useCallback(() => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop();
    }
  }, []);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      void startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  // Hold Spacebar for Push-to-Talk
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (disabled) return;
      if (e.code !== 'Space' || e.repeat) return;
      const target = e.target as HTMLElement | null;
      if (
        target &&
        (['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'].includes(target.tagName) ||
          target.isContentEditable ||
          Boolean(target.closest('.excalidraw-textEditorContainer')))
      ) {
        return;
      }
      e.preventDefault();
      if (!spaceHeldRef.current && !isRecording) {
        spaceHeldRef.current = true;
        void startRecording();
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code !== 'Space') return;
      if (spaceHeldRef.current) {
        e.preventDefault();
        spaceHeldRef.current = false;
        stopRecording();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [disabled, isRecording, startRecording, stopRecording]);

  useEffect(() => {
    return () => {
      clearTimer();
      stopTracks();
    };
  }, [clearTimer, stopTracks]);

  // Spec: amber at 2:30 (150s), red at 3:30 (210s)
  const turnLengthStatus: TurnLengthStatus =
    recordingSeconds >= 210 ? 'red' : recordingSeconds >= 150 ? 'amber' : 'normal';

  return {
    isRecording,
    recordingSeconds,
    turnLengthStatus,
    micError,
    startRecording,
    stopRecording,
    toggleRecording,
  };
}
