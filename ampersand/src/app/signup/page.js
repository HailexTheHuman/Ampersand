export default function Page() {
    return(
        <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
            <main className="flex flex-1 w-full max-w-3xl flex-col items-center py-32 px-16 bg-white dark:bg-black">
                <form className="flex flex-col items-center text-center justify-between w-[60%] border-1 outline-grey-600 border-grey-600 rounded-md">
                    <div className="w-full">
                        <label htmlFor="username" className="mr-[12%]">username</label>
                        <input type="text" name="username" id="username" placeholder="username" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[6%]"/>
                    </div>
                    <div className="w-full">
                        <label htmlFor="email" className="mr-[18%]">email</label>
                        <input type="text" name="email" id="email" placeholder="email" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[9%]"/>
                    </div>
                    <div className="w-full">
                        <label htmlFor="password" className="mr-[13%]">password</label>
                        <input type="text" name="password" id="password" placeholder="password" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[6%]"/>
                    </div>
                    <div className="w-full">
                        <label htmlFor="passconfirm" className="mr-[2%]">confirm password</label>
                        <input type="text" name="passconfirm" id="passconfirm" placeholder="passconfirm" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[2%]"/>
                    </div>
                    <div className="w-full">
                        <input type="submit" name="submit" id="submit" className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                    </div>
                </form>
            </main>
        </div>
    )
}