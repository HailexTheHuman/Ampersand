"use client"

import { useEffect, useState } from "react";

export function clientZone() {
    const [detectedZone, setDetectedZone] = useState(null);

    useEffect(() => {
        const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        setDetectedZone(zone);
    }, []);

    // return (
    //     <div>
    //         {detectedZone && <p>Detected Timezone: {detectedZone}</p>}
    //     </div>
    // );
    return detectedZone;
}