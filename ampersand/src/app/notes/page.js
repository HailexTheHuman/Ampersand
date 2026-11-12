import { addNote } from "@/components/addNote";
import { SendNoteForm } from "@/components/sendNotesForm";
import { AuthorOptions } from "@/components/authorOptions";
import { ListNotes } from "@/components/listNotes"
import { cookies } from "next/headers"
import { redirect } from "next/navigation"
export const instant = false;
export default async function Page() {
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value

    const respone = await fetch(`https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/canPredict?username=${username}`);
    let jsonRes = await respone.json()
    const canPredict = jsonRes.can_predict

    if (!username) redirect("/login")

    return (
        <main className="flex sm:flex-row flex-col max-h-[75%] sm:h-[75%] h-full">
            <div className="flex flex-col w-full h-full order-first sm:order-last">
                {canPredict && <a href="/identityCrisis" className="text-center">Who am I?</a>}
                <SendNoteForm username={username} sendNote={addNote} notBlurry={true}><AuthorOptions/></SendNoteForm>
            </div>
            <ListNotes username={username} className="order-last sm:order-first"/>
        </main>
    )
}