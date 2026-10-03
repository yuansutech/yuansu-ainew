interface User {
    id: number;
    name: string;
    email: string;
}

interface ApiResponse<T> {
    data: T;
    status: number;
    message: string;
}

class ApiClient {
    private baseUrl: string;
    private headers: Record<string, string>;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
        this.headers = { "Content-Type": "application/json" };
    }

    async get<T>(path: string): Promise<ApiResponse<T>> {
        const response = await fetch(`${this.baseUrl}${path}`, {
            headers: this.headers,
        });

        const data = await response.json();
        return {
            data: data as T,
            status: response.status,
            message: response.statusText,
        };
    }

    async post<T>(path: string, body: unknown): Promise<ApiResponse<T>> {
        const response = await fetch(`${this.baseUrl}${path}`, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify(body),
        });

        const data = await response.json();
        return { data, status: response.status, message: response.statusText };
    }

    setAuthToken(token: string): void {
        this.headers["Authorization"] = `Bearer ${token}`;
    }
}

async function loadUsers(client: ApiClient): Promise<User[]> {
    const response = await client.get<User[]>("/users");
    return response.data;
}

async function main() {
    const client = new ApiClient("https://api.example.com");
    client.setAuthToken("secret-token");

    const users = await loadUsers(client);
    users.forEach((user) => {
        console.log(`${user.id}: ${user.name} <${user.email}>`);
    });

    const first: User = users[0];
    console.log(first.name.toUpperCase());

    const response = await client.post<User>("/users", {
        name: "New User",
        email: "new@example.com",
    });

    console.log(response.data.id);
    console.log(response.status.toString());
}

main();