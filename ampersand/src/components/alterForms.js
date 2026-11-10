"use client"

import { redirect } from "next/navigation";


async function addAlter(formdata, username) {
    if (formdata.name && formdata.description) {
        const respone = await fetch('https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/alter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username:username,  alter_name:formdata.name, description: formdata.description })
        });
        let resJson = await respone.json()
        let status = await respone.status
        if (resJson.message == "Alter created successfully") {
            redirect('/profile')
        }
    }
}

function getAddFormData() {
    let name = document.getElementById('name').value;
    let description = document.getElementById('description').value;
    return { name, description};
}

export function AddAlterForm({ username }) {
    
    return(
        <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black sm:max-w-[40%] ml-[9%] sm:max-h-[90%]">
            {/* <h3 id="message"></h3> */}
            <form className="flex flex-col items-center text-center  min-w-[70%] min-h-[35%] border-1 outline-gray-600 border-gray-600 rounded-md" action={() => addAlter(getAddFormData(), username)}>
                <div className="w-full max-h-[40%] min-h-[20%] sm:mt-[14%]">
                    <label htmlFor="name" className="">name</label>
                    <input type="text" name="name" id="name" placeholder="name" className="border-2 outline-purple-700 border-purple-700 rounded-md sm:ml-[13%]" required/>
                </div>
                <div className="w-full max-h-[40%] min-h-[20%] ">
                    <label htmlFor="description" className="">description</label>
                    <input type="text" name="description" id="description" placeholder="description" className="border-2 outline-purple-700 border-purple-700 rounded-md sm:ml-[2%]" required/>
                </div>
                <div className="w-full max-h-[40%] min-h-[20%] ">
                    <input type="submit" name="submit" id="submit" value={"Add alter"} className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
            </form>
        </div>
    )
}

async function editAlter(formdata, username) {
    if (formdata.oldName && (formdata.description || formdata.newName)) {
        const respone = await fetch('https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/alter', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username:username,  old_name:formdata.oldName, new_name:formdata.newName, description: formdata.description })
        });
        let resJson = await respone.json()
        let status = await respone.status
        if (resJson.message == "Alter edited successfully") {
            redirect('/profile')
        }
    }
}

function getEditFormData() {
    let oldName = document.getElementById('oldName').value;
    let newName = document.getElementById('newName').value;
    let description = document.getElementById('descriptionEdit').value;
    return { oldName, newName, description};
}

export function EditAlterForm({ username }) {
    
    return(
        <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black sm:max-w-[40%] ml-[2%] sm:max-h-[90%]">
            {/* <h3 id="message"></h3> */}
            <form className="flex flex-col items-center text-center  min-w-[70%] min-h-[35%] border-1 outline-gray-600 border-gray-600 rounded-md" action={() => editAlter(getEditFormData(), username)}>
                <div className="w-full max-h-[30%] min-h-[20%] sm:mt-[7%]">
                    <label htmlFor="oldName" className="">old name</label>
                    <input type="text" name="oldName" id="oldName" placeholder="old name" className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
                <div className="w-full max-h-[30%] min-h-[20%] ">
                    <label htmlFor="newName" className="">new name</label>
                    <input type="text" name="newName" id="newName" placeholder="new name (not required)" className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
                <div className="w-full max-h-[30%] min-h-[20%] ">
                    <label htmlFor="description" className="">description</label>
                    <input type="text" name="descriptionEdit" id="descriptionEdit" placeholder="description (not required)" className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
                <div className="w-full max-h-[30%] min-h-[20%] ">
                    <input type="submit" name="submit" id="submit" value={"Edit alter"} className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
            </form>
        </div>
    )
}