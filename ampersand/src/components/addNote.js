"use server"

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";


export async function addNote(formData) {

    const username = (await cookies()).get("username")?.value
    const note = formData.get("note")
    const author = formData.get("author")
    if (!username || !note || !author) return

    if (note && author) {
        console.log('adding note...')
        console.log("form stuffs ", JSON.stringify({ username:username, note: note, author: author }))
        const respone = await fetch('http://localhost:8080/note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username:username, note: note, author: author })
        });
        console.log('frontend add note')
        // let resJson = await respone.json()
        let status = await respone.status
        // console.log("resJson", resJson)
        // console.log("status", status)
        if (status == 201) {
            revalidatePath('/notes')
            // redirect("/notes")
            // const router = useRouter()
            // router.refresh
        }
    }
}