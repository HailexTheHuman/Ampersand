import { AddNoteForm } from "@/components/addNotesForm";
import { AuthorOptions } from "@/components/authorOptions";
import { ListNotes } from "@/components/listNotes"
import { cookies } from "next/headers"
import { redirect } from "next/navigation"
export const instant = false;
export default async function Page() {
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value

    if (!username) redirect("/login")

    return (
        <main className="flex flex-row max-h-[90%]">
            <ListNotes username={username}/>
            <AddNoteForm username={username}/>
        </main>
    )
}