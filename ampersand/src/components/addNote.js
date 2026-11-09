"use server"

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";


export async function getCurrentTimestampWithOffset() {
    const d = new Date();
    const pad = n => String(Math.abs(n)).padStart(2, '0');
    const off = -d.getTimezoneOffset(); // minutes east of UTC
    const sign = off >= 0 ? '+' : '-';

    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
        `T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` +
        `${sign}${pad(Math.trunc(off / 60))}:${pad(off % 60)}`;
}


export async function addNote(prevstate, formData) {
    const username = (await cookies()).get("username")?.value
    const note = formData.get("note")
    const author = formData.get("author")
    const time = await getCurrentTimestampWithOffset()
    if (!username || !note || !author) return

    if (note && author) {
        const respone = await fetch('https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username:username, note: note, author: author, time:time })
        });
        let resJson = await respone.json()
        let status = await respone.status
        if (status == 201) {
            revalidatePath('/notes')
        }
        return {predictions:false, most_likely:false, total:0}
    }
}