export type KernelRequest =
  | {
      type: "SIMULATE_SHOT";
      payload: {
        world: any;
        steps: number;
        dt: number;
      };
    }
  | {
      type: "SUBMIT_SCORE";
      payload: {
        user: string;
        strokes: number;
        optimalDistance: number;
        actualDistance: number;
        precision: number;
      };
    }
  | {
      type: "VALIDATE_REPLAY";
      payload: {
        replay: any;
        clientFinal: any;
      };
    };

export type KernelResponse = {
  success: boolean;
  data?: any;
  error?: string;
};
