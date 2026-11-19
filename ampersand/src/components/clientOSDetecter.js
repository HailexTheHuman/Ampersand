'use client';

import { useEffect, useState } from 'react';

export function osDetector() {
    const [os, setOs] = useState('Unknown');

    useEffect(() => {
        const ua = window.navigator.userAgent;
        if (/Windows/i.test(ua)) setOs('Windows');
        else if (/iPhone|iPad|iPod/i.test(ua)) setOs('iOS');
        else if (/Mac/i.test(ua)) setOs('macOS');
        else if (/Android/i.test(ua)) setOs('Android');
        else if (/Linux/i.test(ua)) setOs('Linux');
        else setOs('Unknown');
    }, []);

    return os;
}