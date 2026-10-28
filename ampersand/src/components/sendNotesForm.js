"use client"

import { Children, useActionState, useState } from "react";
// import { AuthorOptions } from "./authorOptions";


const initialState = {
    predictions: undefined,
    most_likely: undefined,
    total: 0.0
};


export function SendNoteForm({ username, sendNote, notBlurry, children }) {

    const [state, formAction, isPending] = useActionState(sendNote, initialState);

    let stylingDiv = notBlurry ? "flex flex-1 w-full max-w-[64%] max-h-[90%] flex-col justify-center items-center py-32 px-16 bg-white dark:bg-black ml-[2%]" : "flex flex-1 w-full max-w-[100%] h-[90%] flex-col justify-center items-center py-32 px-16 bg-white dark:bg-black ml-[2%]"
    let stylingForm = notBlurry ? "flex flex-col items-center text-center justify-between border-1 outline-gray-600 border-gray-600 rounded-md min-w-[55%] min-h-[55%]" : "flex flex-col items-center text-center justify-between border-1 outline-gray-600 border-gray-600 rounded-md min-w-[55%] min-h-[75%]"
    return(
        <div className={stylingDiv}>
            <div className="flex flex-row items-center text-center justify-between w-[75%] max-h-[20%] max-w-[90%]">
                <h3 id="message"></h3>
                {state.predictions && state.predictions.map((prediction) => (
                    <div className="flex flex-col" key={prediction.name} >
                        <h3 >{prediction.name}</h3>
                        {prediction.likelyhood >= 0.10 &&
                            <h3 >{(prediction.likelyhood*100).toPrecision(4)}%</h3>
                        }
                        {prediction.likelyhood < 0.10 &&
                            <h3 >{(prediction.likelyhood*100).toPrecision(3)}%</h3>
                        }
                    </div>
                ))}
                {state.most_likely && 
                <div>
                    <h3>most likely: {state.most_likely}</h3>
                </div>
                    }
            </div>
            <form className={stylingForm} action={formAction}>
                <div className="w-full flex items-center w-[75%] h-[75%] max-h-[90%] max-w-[90%]">
                    <label htmlFor="note" className="w-[15%]">note</label>
                    <textarea name="note" id="note" className="border-2 outline-purple-700 border-purple-700 rounded-md min-w-[25%] min-h-[25%] w-[75%] h-[75%] resize max-w-[90%] max-h-[75%]" required/>
                </div>
                {notBlurry &&
                <div className="w-full">
                    <label htmlFor="author" className="mr-[3%]">author</label>
                    {/* <AuthorOptions username={username}/> */}
                    {children}
                </div>
                }
                <div className="w-full h-[15%] mt-[3%]">
                    <input type="submit" name="submit" id="submit" value={notBlurry ? "Post Note":"Predict"} className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
            </form>
        </div>
    )
}