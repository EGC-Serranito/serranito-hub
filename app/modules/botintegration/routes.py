from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.modules.botintegration.services import NodeService
from app.modules.botintegration import botintegration_bp
from app.modules.botintegration.forms import BotIntegrationForm
from app.modules.botintegration.models import TreeNode
from app import db

# Instancia del servicio de nodos
tree_node_service = NodeService()

'''
GET /botintegration
Obtiene el árbol de nodos para un usuario específico.
'''

@botintegration_bp.route('/botintegration', methods=['GET'])
@login_required
def index():
    form = BotIntegrationForm()
    tree = tree_node_service.get_tree_nodes_by_user(current_user.id)
    if not tree:
        tree = []
    else:
        tree=tree[0].to_dict()
    
    return render_template('botintegration/index.html', tree=tree, form=form)

@botintegration_bp.route('/botintegration/add-bot', methods=['GET', 'POST'])
@login_required
def create_node_route_add_bot():
    form = BotIntegrationForm()
    parent_id = form.parent_id.data  # ID del nodo padre
    name = form.name.data  # Nombre del nuevo nodo
    user_id = current_user.id
    single_child = False  # Valor por defecto, ajustable según sea necesario

    # Iniciar el path con el ID del usuario
    path = f"{user_id}/{name}"

    if parent_id:
        parent = TreeNode.query.get(parent_id)
        if parent:
            path = f"{parent.path}/{name}"

    try:
        result = tree_node_service.create_node_route_add_bot(user_id=user_id, name=name, parent_id=parent_id, path=path, single_child=single_child)

        return tree_node_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='botintegration.index',
            success_msg='Chat created successfully!',
            error_template='botintegration/index.html',
            form=form
        )
            
        # Actualizar el árbol de nodos
        tree = tree_node_service.get_tree_nodes_by_user(current_user.id)
        
        # Redirigir a la vista que muestra el árbol de nodos
        return render_template('botintegration/index.html', tree=tree[0].to_dict(), form=form)
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear el nodo: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))

@botintegration_bp.route('/botintegration/add-chat', methods=['GET', 'POST'])
@login_required
def create_node_route_add_chat():
    form = BotIntegrationForm()
    parent_id = form.parent_id.data  # ID del nodo padre
    name = form.name.data  # Nombre del nuevo nodo
    user_id = current_user.id
    single_child = False  # Valor por defecto, ajustable según sea necesario

    # Iniciar el path con el ID del usuario
    path = f"{user_id}/{name}"

    if parent_id:
        parent = TreeNode.query.get(parent_id)
        if parent:
            path = f"{parent.path}/{name}"

    try:
        result = tree_node_service.create_node_route_add_chat(user_id=user_id, name=name, parent_id=parent_id, path=path, single_child=single_child)

        return tree_node_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='botintegration.index',
            success_msg='Chat created successfully!',
            error_template='botintegration/index.html',
            form=form
        )
            
        # Actualizar el árbol de nodos
        tree = tree_node_service.get_tree_nodes_by_user(current_user.id)
        
        # Redirigir a la vista que muestra el árbol de nodos
        return render_template('botintegration/index.html', tree=tree[0].to_dict(), form=form)
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear el nodo: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))

@botintegration_bp.route('/botintegration/add-types-notification', methods=['GET', 'POST'])
@login_required
def create_node_route_add_types_notification():
    form = BotIntegrationForm()
    parent_id = form.parent_id.data  # ID del nodo padre
    name = form.name.data  # Nombre del nuevo nodo
    user_id = current_user.id
    single_child = False  # Valor por defecto, ajustable según sea necesario

    # Iniciar el path con el ID del usuario
    path = f"{user_id}/{name}"

    if parent_id:
        parent = TreeNode.query.get(parent_id)
        if parent:
            path = f"{parent.path}/{name}"

    try:
        result = tree_node_service.create_node_route_add_types_notification(user_id=user_id, name=name, parent_id=parent_id, path=path, single_child=single_child)

        return tree_node_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='botintegration.index',
            success_msg='Chat created successfully!',
            error_template='botintegration/index.html',
            form=form
        )
            
        # Actualizar el árbol de nodos
        tree = tree_node_service.get_tree_nodes_by_user(current_user.id)
        
        # Redirigir a la vista que muestra el árbol de nodos
        return render_template('botintegration/index.html', tree=tree[0].to_dict(), form=form)
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear el nodo: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))

@botintegration_bp.route('/botintegration/add-feature', methods=['GET', 'POST'])
@login_required
def create_node_route_add_feature():
    form = BotIntegrationForm()
    parent_id = form.parent_id.data  # ID del nodo padre
    name = form.name.data  # Nombre del nuevo nodo
    user_id = current_user.id
    single_child = False  # Valor por defecto, ajustable según sea necesario

    # Iniciar el path con el ID del usuario
    path = f"{user_id}/{name}"

    if parent_id:
        parent = TreeNode.query.get(parent_id)
        if parent:
            path = f"{parent.path}/{name}"

    try:
        result = tree_node_service.create_node_route_add_feature(user_id=user_id, name=name, parent_id=parent_id, path=path, single_child=single_child)

        return tree_node_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='botintegration.index',
            success_msg='Chat created successfully!',
            error_template='botintegration/index.html',
            form=form
        )
            
        # Actualizar el árbol de nodos
        tree = tree_node_service.get_tree_nodes_by_user(current_user.id)
        
        # Redirigir a la vista que muestra el árbol de nodos
        return render_template('botintegration/index.html', tree=tree[0].to_dict(), form=form)
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear el nodo: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))

@botintegration_bp.route('/botintegration/delete/<int:node_id>', methods=['POST'])
@login_required
def delete_node(node_id):
    try:
        # Obtener el nodo usando el servicio
        node = tree_node_service.get_or_404(node_id)

        # Verificar si el usuario tiene permiso para eliminar el nodo
        if node.user_id != current_user.id:
            flash('You are not authorized to delete this node', 'error')
            return redirect(url_for('botintegration.index'))

        # Llamar al servicio para eliminar el nodo
        result = tree_node_service.delete_node(node_id)
        
        # Retroalimentación del resultado de la eliminación
        if result:
            flash('Node deleted successfully!', 'success')
        else:
            flash('Error deleting node', 'error')
        
        return redirect(url_for('botintegration.index'))

    except Exception as e:
        # En caso de error, mostramos un mensaje de error
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')

    # Redirigir a la página de índice después de intentar eliminar
    return redirect(url_for('botintegration.index'))

@botintegration_bp.route('/botintegration/merge-config/<int:node_id>', methods=['POST'])
@login_required
def merge_config(node_id):
    try:
        # Obtener el nodo usando el servicio
        node = tree_node_service.get_or_404(node_id)

        # Verificar si el usuario tiene permiso para eliminar el nodo
        if node.user_id != current_user.id:
            flash('You are not authorized to delete this node', 'error')
            return redirect(url_for('botintegration.index'))

        # Llamar al servicio para eliminar el nodo
        result = tree_node_service.delete_node(node_id)
        
        # Retroalimentación del resultado de la eliminación
        if result:
            flash('Node deleted successfully!', 'success')
        else:
            flash('Error deleting node', 'error')
        
        return redirect(url_for('botintegration.index'))

    except Exception as e:
        # En caso de error, mostramos un mensaje de error
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')

    # Redirigir a la página de índice después de intentar eliminar
    return redirect(url_for('botintegration.index'))