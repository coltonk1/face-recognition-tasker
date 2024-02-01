import type { NextApiRequest, NextApiResponse } from "next";
import { spawn } from "child_process";

interface ApiResponse {
    result: string;
    exitCode: number | null;
}

export default function handler(req: NextApiRequest, res: NextApiResponse<ApiResponse>) {
    function get_uuid() {
        const childProcess = spawn("python", ["./python/controller.py", "-get_uuid", req.body.name]);

        let result = "";

        childProcess.stdout.on("data", (data) => {
            result += data.toString();
        });

        childProcess.stderr.on("data", (data) => {
            result += data.toString();
        });

        childProcess.on("close", (code) => {
            const response: ApiResponse = {
                result,
                exitCode: code,
            };
            res.status(200).json(response);
        });
    }

    get_uuid();

    // res.status(200).json({ name: "J Doe" });
}
