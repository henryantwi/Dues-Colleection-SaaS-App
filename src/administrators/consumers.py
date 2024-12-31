import json

from channels.generic.websocket import AsyncWebsocketConsumer


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.department = self.scope["url_route"]["kwargs"].get("department")
        self.group_name = (
            f"dashboard_{self.department}" if self.department else "dashboard_all"
        )

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "update_dashboard",
                "data": data,
            },
        )

    async def update_dashboard(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))
