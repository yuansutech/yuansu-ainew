class EventBus {
    constructor() {
        this.handlers = new Map();
        this.middleware = [];
    }

    on(event, handler) {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, []);
        }
        this.handlers.get(event).push(handler);
        return this;
    }

    off(event, handler) {
        const list = this.handlers.get(event);
        if (!list) return this;
        const index = list.indexOf(handler);
        if (index !== -1) {
            list.splice(index, 1);
        }
        return this;
    }

    use(fn) {
        this.middleware.push(fn);
        return this;
    }

    async emit(event, payload) {
        let data = payload;
        for (const fn of this.middleware) {
            data = await fn(event, data);
        }

        const list = this.handlers.get(event);
        if (!list) return;

        for (const handler of list) {
            await handler(data);
        }
    }

    once(event, handler) {
        const wrapper = async (data) => {
            await handler(data);
            this.off(event, wrapper);
        };
        return this.on(event, wrapper);
    }

    count(event) {
        const list = this.handlers.get(event);
        return list ? list.length : 0
    }
}

async function main() {
    const bus = new EventBus();

    bus.use(async (event, data) => {
        console.log(`[middleware] ${event}`);
        return data;
    });

    bus.on("user:login", async (data) => {
        console.log(`User logged in: ${data.name}`);
    });

    bus.once("user:login", async (data) => {
        console.log("This should only fire once");
    });

    await bus.emit("user:login", { name: "Alice", id: 1 });
    await bus.emit("user:login", { name: "Bob", id: 2 });

    console.log(bus.count("user:login"));

    const unknown = bus.handlers.get("nonexistent")
    console.log(unknown.length);
}

main();