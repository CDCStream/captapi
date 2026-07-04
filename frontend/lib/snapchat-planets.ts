// Snapchat Plus "Friend Solar System": your closeness to a friend is shown as
// a planet. Mercury (closest to the sun) = the tightest friend, Neptune the
// most distant of the eight. The "sun" is the person whose system you are in.

export interface Planet {
  order: number;
  name: string;
  emoji: string;
  color: string; // tailwind bg for the orb
  meaning: string;
}

export const SNAP_PLANETS: Planet[] = [
  {
    order: 1,
    name: "Mercury",
    emoji: "\u2764\uFE0F",
    color: "bg-red-500",
    meaning:
      "Your #1 best friend. Mercury is closest to the sun, so this planet marks the person you interact with the most. It appears as a red planet ringed with red hearts.",
  },
  {
    order: 2,
    name: "Venus",
    emoji: "\u{1F49B}",
    color: "bg-amber-400",
    meaning:
      "Your #2 best friend. Venus is a tan planet surrounded by yellow, blue, and pink hearts \u2014 you are one of their closest people, just behind their top spot.",
  },
  {
    order: 3,
    name: "Earth",
    emoji: "\u{1F499}",
    color: "bg-blue-500",
    meaning:
      "Your #3 best friend. Earth is the blue-and-green planet with red hearts and a tiny moon \u2014 a solid, high-ranking friendship.",
  },
  {
    order: 4,
    name: "Mars",
    emoji: "\u{1F49C}",
    color: "bg-red-700",
    meaning:
      "Your #4 best friend. Mars is a reddish-brown planet ringed with purple and blue hearts and stars.",
  },
  {
    order: 5,
    name: "Jupiter",
    emoji: "\u{1F9E1}",
    color: "bg-orange-400",
    meaning:
      "Your #5 best friend. Jupiter is an orange, reddish-brown planet with no hearts \u2014 still a close friend, just further out in the system.",
  },
  {
    order: 6,
    name: "Saturn",
    emoji: "\u{1FA90}",
    color: "bg-yellow-500",
    meaning:
      "Your #6 best friend. Saturn is the orange planet with its iconic ring, surrounded by stars \u2014 a meaningful but more distant friendship.",
  },
  {
    order: 7,
    name: "Uranus",
    emoji: "\u{1F49A}",
    color: "bg-teal-400",
    meaning:
      "Your #7 best friend. Uranus is a green planet with no hearts, sitting near the edge of the top-eight friends.",
  },
  {
    order: 8,
    name: "Neptune",
    emoji: "\u{1F535}",
    color: "bg-blue-700",
    meaning:
      "Your #8 best friend. Neptune is the deep-blue planet farthest from the sun \u2014 you made the top eight, but it is the most distant spot in the solar system.",
  },
];
