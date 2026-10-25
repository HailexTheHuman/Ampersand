// "use server"

export async function ListNotes({ username }) {
    console.log("username: ", username)
    let results = await fetch(`http://localhost:8080/notes?username=${encodeURIComponent(username)}`, { cache: "no-store"})
    let notesJ = await results.json();
    console.log("notesJ: ", notesJ)
    let notes = notesJ.notes
    
    return (
        <div className="flex flex-col items-center text-center justify-between w-[34%] border-1 outline-gray-600 border-gray-600 rounded-md overflow-y-auto overscroll-y-auto max-h-[90%] scrollbar-track-purple-100/0 scrollbar-thumb-purple-600 ">
            {notesJ.error && <p>error: {notesJ.error}</p>}
            {await notes && notes.map((note) => (
                <div key={note.note_id} className="flex flex-col items-center text-center justify-between w-full border-1 outline-gray-600 border-gray-600 rounded-md">
                    <p>note: {note.note}</p>
                    {note.author && <p>author: {note.author}</p>}
                    {note.time && <p>time: {new Date(note.time).toLocaleString()}</p>}
                </div>
            ))}
        </div>
    )
}