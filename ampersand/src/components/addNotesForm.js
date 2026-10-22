import { addNote } from "./addNote";
import { AuthorOptions } from "./authorOptions";


// function getFormData() {
//     let note = document.getElementById('author').value;
//     let author = document.getElementById('author').value;
//     return { username, email };
// }

export function AddNoteForm({ username }) {
    return(
        // <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
        <div className="flex flex-1 w-full max-w-[64%] max-h-[90%] flex-col justify-center items-center py-32 px-16 bg-white dark:bg-black ml-[2%]">
            <h3 id="message"></h3>
            <form className="flex flex-col items-center text-center justify-between border-1 outline-gray-600 border-gray-600 rounded-md min-w-[55%] min-h-[55%]" action={addNote}>
                <div className="w-full flex items-center w-[75%] h-[75%]">
                    <label htmlFor="note" className="w-[15%]">note</label>
                    <textarea name="note" id="note" className="border-2 outline-purple-700 border-purple-700 rounded-md w-[75%] h-[75%] resize" required/>
                </div>
                <div className="w-full">
                    <label htmlFor="author" className="mr-[3%]">author</label>
                    <AuthorOptions username={username}/>
                </div>
                <div className="w-full">
                    <input type="submit" name="submit" id="submit" value={"Post Note"} className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
            </form>
        </div>
    )
}