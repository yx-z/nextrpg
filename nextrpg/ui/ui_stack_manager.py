from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent
from nextrpg.scene.scene import Scene

if TYPE_CHECKING:
    from nextrpg.ui.widget_on_screen import WidgetOnScreen


class UILayerType(Enum):
    """Types of UI layers with different behaviors."""
    BACKGROUND = auto()  # Always rendered, events pass through
    NORMAL = auto()      # Standard UI layer
    OVERLAY = auto()     # Rendered on top, blocks events to lower layers
    MODAL = auto()       # Blocks all events to lower layers, dims background
    POPUP = auto()       # Non-modal overlay that can be dismissed


@dataclass(frozen=True)
class UILayer:
    """Represents a single UI layer in the stack."""
    id: str
    layer_type: UILayerType
    widget_on_screen: WidgetOnScreen
    z_order: int = 0
    is_active: bool = True
    dim_background: bool = False  # For modal layers
    
    def tick(self, time_delta: Millisecond) -> Self:
        """Update the layer's widget."""
        widget_on_screen = self.widget_on_screen.tick(time_delta)
        return replace(self, widget_on_screen=widget_on_screen)
    
    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        """Get all drawing elements for this layer."""
        return self.widget_on_screen.drawing_on_screens
    
    def event(self, event: IoEvent) -> Self | Scene | None:
        """Handle events for this layer."""
        if not self.is_active:
            return self
        
        result = self.widget_on_screen.event(event)
        if isinstance(result, Scene):
            return result
        elif result is not None:
            return replace(self, widget_on_screen=result)
        return self


@dataclass(frozen=True)
class UIStackManager:
    """Manages a stack of UI layers with proper z-ordering and event handling."""
    layers: tuple[UILayer, ...] = ()
    
    def add_layer(
        self, 
        layer_id: str, 
        widget_on_screen: WidgetOnScreen,
        layer_type: UILayerType = UILayerType.NORMAL,
        z_order: int = 0,
        dim_background: bool = False
    ) -> Self:
        """Add a new layer to the stack."""
        # Remove existing layer with same ID if it exists
        existing_layers = tuple(
            layer for layer in self.layers 
            if layer.id != layer_id
        )
        
        new_layer = UILayer(
            id=layer_id,
            layer_type=layer_type,
            widget_on_screen=widget_on_screen,
            z_order=z_order,
            dim_background=dim_background
        )
        
        # Sort layers by z_order (higher values on top)
        all_layers = existing_layers + (new_layer,)
        sorted_layers = tuple(
            sorted(all_layers, key=lambda l: l.z_order)
        )
        
        return replace(self, layers=sorted_layers)
    
    def remove_layer(self, layer_id: str) -> Self:
        """Remove a layer from the stack."""
        remaining_layers = tuple(
            layer for layer in self.layers 
            if layer.id != layer_id
        )
        return replace(self, layers=remaining_layers)
    
    def get_layer(self, layer_id: str) -> UILayer | None:
        """Get a layer by its ID."""
        for layer in self.layers:
            if layer.id == layer_id:
                return layer
        return None
    
    def set_layer_active(self, layer_id: str, is_active: bool) -> Self:
        """Set whether a layer is active."""
        updated_layers = []
        for layer in self.layers:
            if layer.id == layer_id:
                updated_layers.append(replace(layer, is_active=is_active))
            else:
                updated_layers.append(layer)
        return replace(self, layers=tuple(updated_layers))
    
    def bring_to_front(self, layer_id: str) -> Self:
        """Bring a layer to the front by setting its z_order to the highest."""
        if not self.layers:
            return self
        
        max_z_order = max(layer.z_order for layer in self.layers)
        updated_layers = []
        for layer in self.layers:
            if layer.id == layer_id:
                updated_layers.append(replace(layer, z_order=max_z_order + 1))
            else:
                updated_layers.append(layer)
        
        # Re-sort layers
        sorted_layers = tuple(
            sorted(updated_layers, key=lambda l: l.z_order)
        )
        return replace(self, layers=sorted_layers)
    
    def tick(self, time_delta: Millisecond) -> Self:
        """Update all layers."""
        updated_layers = tuple(layer.tick(time_delta) for layer in self.layers)
        return replace(self, layers=updated_layers)
    
    def event(self, event: IoEvent) -> Self | Scene | None:
        """Handle events, starting from the top layer."""
        # Process layers from top to bottom
        for layer in reversed(self.layers):
            if not layer.is_active:
                continue
                
            result = layer.event(event)
            if isinstance(result, Scene):
                return result
            elif result is not None:
                # Update the layer and return updated stack
                updated_layers = []
                for l in self.layers:
                    if l.id == layer.id:
                        updated_layers.append(result)
                    else:
                        updated_layers.append(l)
                return replace(self, layers=tuple(updated_layers))
            
            # If this layer blocks events to lower layers, stop processing
            if layer.layer_type in (UILayerType.MODAL, UILayerType.OVERLAY):
                break
        
        return self
    
    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        """Get all drawing elements from all layers, properly ordered."""
        all_drawings = []
        
        # Add background dimming for modal layers
        modal_layers = [layer for layer in self.layers 
                       if layer.layer_type == UILayerType.MODAL and layer.dim_background]
        
        # Collect drawings from all active layers
        for layer in self.layers:
            if layer.is_active:
                all_drawings.extend(layer.drawing_on_screens)
        
        return tuple(all_drawings)
    
    @property
    def has_modal_layers(self) -> bool:
        """Check if there are any active modal layers."""
        return any(
            layer.is_active and layer.layer_type == UILayerType.MODAL 
            for layer in self.layers
        )
    
    @property
    def top_layer(self) -> UILayer | None:
        """Get the topmost layer."""
        if not self.layers:
            return None
        return max(self.layers, key=lambda l: l.z_order)
