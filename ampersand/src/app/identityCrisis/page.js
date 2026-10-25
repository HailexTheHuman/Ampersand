
import { predict } from "@/components/predict"
import { SendNoteForm } from "@/components/sendNotesForm"
import { cookies } from "next/headers"
import { redirect } from "next/navigation"

export const instant = false;


export default async function Page() {
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value

    if (!username) redirect("/login")

    return (
        <main className="flex flex-row h-full w-full">
            <SendNoteForm username={username} sendNote={predict} notBlurry={false}/>
        </main>
    )
}