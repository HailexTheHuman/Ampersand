"use server"

import { cookies } from "next/headers";

export async function predict(prevState, formData) {

    const username = (await cookies()).get("username")?.value
    const note = formData.get("note")
    if (!username || !note) return

    if (note) {
        // const respone = await fetch('http://localhost:8080/predict', {
        const respone = await fetch('https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username:username, note: note})
        });
        let resJson = await respone.json()
        let total = 0.0
        resJson.predictions.forEach(prediction => {
            total += prediction.likelyhood
        });
        return {predictions:resJson.predictions, most_likely:resJson.most_likely, total}
    }
}