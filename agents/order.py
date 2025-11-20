"""
OrderAgent - Sipariş yönetimi
Creates orders, calculates commission
"""
from agents.base import BaseAgent
from utils.supabase_client import get_supabase_admin
from typing import Dict, Any
from datetime import datetime
import uuid

class OrderAgent(BaseAgent):
    def __init__(self):
        super().__init__("OrderAgent")
        self.supabase = get_supabase_admin()
        self.commission_rate = 0.025  # %2.5
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an order
        State should contain:
        - listing_id: UUID of the listing
        - buyer_id: UUID of the buyer
        - quantity: Number of items (default: 1)
        """
        listing_id = state.get("listing_id")
        buyer_id = state.get("buyer_id")
        quantity = state.get("quantity", 1)
        
        if not listing_id or not buyer_id:
            self.log("Missing listing_id or buyer_id", "error")
            state["order_status"] = "error"
            state["order_message"] = "Sipariş bilgileri eksik"
            return state
        
        self.log(f"Creating order for listing {listing_id}")
        
        try:
            # Get listing details
            listing = self.supabase.table('listings')\
                .select('*')\
                .eq('id', listing_id)\
                .single()\
                .execute()
            
            if not listing.data:
                self.log(f"Listing {listing_id} not found", "error")
                state["order_status"] = "error"
                state["order_message"] = "İlan bulunamadı"
                return state
            
            listing_data = listing.data
            
            # Check if active
            if listing_data['status'] != 'active':
                state["order_status"] = "error"
                state["order_message"] = "Bu ilan artık aktif değil"
                return state
            
            # Check stock
            if listing_data.get('stock', 1) < quantity:
                state["order_status"] = "error"
                state["order_message"] = f"Yeterli stok yok (Mevcut: {listing_data.get('stock', 0)})"
                return state
            
            # Calculate prices
            price = float(listing_data['price'])
            total_price = price * quantity
            commission = total_price * self.commission_rate
            seller_receives = total_price - commission
            
            # Create order
            order_data = {
                "id": str(uuid.uuid4()),
                "listing_id": listing_id,
                "buyer_id": buyer_id,
                "seller_id": listing_data['user_id'],
                "quantity": quantity,
                "price": total_price,
                "commission": commission,
                "seller_receives": seller_receives,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table('orders').insert(order_data).execute()
            
            if result.data:
                order_id = result.data[0]['id']
                
                # Update listing stock
                new_stock = listing_data.get('stock', 1) - quantity
                self.supabase.table('listings')\
                    .update({"stock": new_stock})\
                    .eq('id', listing_id)\
                    .execute()
                
                # If stock is 0, mark as sold
                if new_stock <= 0:
                    self.supabase.table('listings')\
                        .update({"status": "sold"})\
                        .eq('id', listing_id)\
                        .execute()
                
                state["order_status"] = "success"
                state["order_id"] = order_id
                state["order_data"] = {
                    "order_id": order_id,
                    "listing_title": listing_data['title'],
                    "quantity": quantity,
                    "total_price": total_price,
                    "commission": commission,
                    "seller_receives": seller_receives
                }
                state["order_message"] = self._format_order_confirmation(state["order_data"])
                
                self.log(f"Order created: {order_id} (Total: {total_price:.2f} TL)")
            else:
                state["order_status"] = "error"
                state["order_message"] = "Sipariş oluşturulamadı"
            
        except Exception as e:
            self.log(f"Order creation failed: {str(e)}", "error")
            state["order_status"] = "error"
            state["order_message"] = "Sipariş oluşturulurken hata oluştu"
        
        return state
    
    def _format_order_confirmation(self, order_data: Dict) -> str:
        """Format order confirmation message"""
        return f"""✅ Siparişiniz alındı!

📦 **{order_data['listing_title']}**
🔢 Adet: {order_data['quantity']}

💰 Toplam: {order_data['total_price']:,.2f} TL
💵 Satıcıya gidecek: {order_data['seller_receives']:,.2f} TL
🏦 Komisyon: {order_data['commission']:,.2f} TL

📋 Sipariş No: {order_data['order_id'][:8]}

Satıcı ile kısa süre içinde iletişime geçilecektir."""
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order details"""
        try:
            result = self.supabase.table('orders')\
                .select('*, listings(title), buyers:buyer_id(name), sellers:seller_id(name)')\
                .eq('id', order_id)\
                .single()\
                .execute()
            
            return result.data if result.data else None
            
        except Exception as e:
            self.log(f"Failed to get order status: {str(e)}", "error")
            return None
    
    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """
        Update order status
        Statuses: pending, confirmed, shipped, delivered, cancelled
        """
        try:
            update_data = {"status": new_status}
            
            if new_status == "delivered":
                update_data["completed_at"] = datetime.now().isoformat()
            
            self.supabase.table('orders')\
                .update(update_data)\
                .eq('id', order_id)\
                .execute()
            
            self.log(f"Order {order_id} status updated to {new_status}")
            return True
            
        except Exception as e:
            self.log(f"Failed to update order status: {str(e)}", "error")
            return False
