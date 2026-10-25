"use server"

import { cookies } from "next/headers";

export async function predict(prevState, formData) {

    const username = (await cookies()).get("username")?.value
    const note = formData.get("note")
    if (!username || !note) return

    if (note) {
        console.log('adding note...')
        console.log("form stuffs ", JSON.stringify({ username:username, note: note}))
        const respone = await fetch('http://localhost:8080/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username:username, note: note})
        });
        console.log('frontend add note')
        let resJson = await respone.json()
        console.log("resJson", resJson)
        let total = 0.0
        resJson.predictions.forEach(prediction => {
            total += prediction.likelyhood
        });
        return {predictions:resJson.predictions, most_likely:resJson.most_likely, total}
    }
}