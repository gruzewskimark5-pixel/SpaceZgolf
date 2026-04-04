export const db = {
    addScore: (data: { user: string, score: number, timestamp: number }) => {
        // mock DB insert
        console.log("Score inserted", data);
    }
};
