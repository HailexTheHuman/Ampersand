import Image from "next/image";

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
        <p>
          Welcome to Ampersand. Here you can keep track of your alters' names, count, and front history. You can also leave notes for eachother here. If you do you will also be able to use the machine learning model to help figure out who might before fronting, and getting summaries of what you missed with the notes.
        </p>
      </main>
    </div>
  );
}
