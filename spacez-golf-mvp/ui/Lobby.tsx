import React, { useState } from "react";

const avatars = [
  { id: "closer", name: "The Closer", color: "bg-red-500" },
  { id: "ice", name: "Ice Veins", color: "bg-blue-400" },
  { id: "gambler", name: "The Gambler", color: "bg-yellow-400" },
  { id: "bomber", name: "The Bomber", color: "bg-purple-500" }
];

export default function Lobby() {
  const [selectedAvatar, setSelectedAvatar] = useState<any>(null);
  const [queueing, setQueueing] = useState(false);
  const [match, setMatch] = useState<any>(null);

  const findMatch = () => {
    setQueueing(true);

    setTimeout(() => {
      setMatch({
        opponent: "PlayerX",
        avatar: "Ice Veins",
        rating: 1380
      });
      setQueueing(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <h1 className="text-3xl font-bold mb-6">SpaceZ Lobby</h1>

      {/* Avatar Selection */}
      <div className="mb-6">
        <h2 className="text-xl mb-2">Choose Your Avatar</h2>
        <div className="flex gap-4">
          {avatars.map((a) => (
            <div
              key={a.id}
              onClick={() => setSelectedAvatar(a)}
              className={`p-4 rounded-xl cursor-pointer ${
                selectedAvatar?.id === a.id ? "border-2 border-white" : ""
              } ${a.color}`}
            >
              {a.name}
            </div>
          ))}
        </div>
      </div>

      {/* Queue Button */}
      <button
        onClick={findMatch}
        disabled={!selectedAvatar || queueing}
        className="bg-green-500 px-6 py-3 rounded-xl font-bold disabled:opacity-50"
      >
        {queueing ? "Finding Match..." : "Start Match"}
      </button>

      {/* Match Found */}
      {match && (
        <div className="mt-8 p-4 bg-zinc-800 rounded-xl">
          <h2 className="text-xl mb-2">Match Found</h2>
          <div>Opponent: {match.opponent}</div>
          <div>Avatar: {match.avatar}</div>
          <div>Rating: {match.rating}</div>
        </div>
      )}
    </div>
  );
}
