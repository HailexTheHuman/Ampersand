"use client"

import { useEffect, useState } from "react";

export function ClientZone({ note }) {
    const [detectedZone, setDetectedZone] = useState(null);

    useEffect(() => {
        const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        setDetectedZone(zone);
    }, []);

    return (
        detectedZone && <p>time: {new Date(note.time).toLocaleString(undefined, { timeZone: detectedZone })}</p>
    );
    // return detectedZone;
}