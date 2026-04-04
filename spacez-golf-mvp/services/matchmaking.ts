import { Player } from "../engine/heat";

export function findMatch(player: Player, pool: Player[]) {
  return pool.find(p => {
    const ratingDiff = Math.abs(p.rating - player.rating);

    return (
      ratingDiff < 150 && // fair match
      p.id !== player.id
    );
  });
}
