"use server"

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { getCurrentTimestampWithOffset } from "./addNote";


export async function SetFront(formData) {
    const username = (await cookies()).get("username")?.value
    const alter_name = formData.get("name")
    const time = await getCurrentTimestampWithOffset()
    console.log("set front info: ", JSON.stringify({ username:username, alter_name:alter_name, time:time }))
    const respone = await fetch('http://localhost:8080/front', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username:username, alter_name:alter_name, time:time })
    });
    let responeJ = await respone.json()
    let status = respone.status
    console.log("response: ", responeJ)
    if (status == 201) {
        revalidatePath('/profile')
    }
}