from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.modules.botintegration.services import NodeService
from app.modules.botintegration import botintegration_bp
from app.modules.botintegration.forms import BotIntegrationForm
from app.modules.botintegration.models import TreeNode
from app import db

# Instancia del servicio de nodos
tree_node_service = NodeService()


@botintegration_bp.route('/botintegration', methods=['GET'])
@login_required
def index():
    """Obtiene el árbol de nodos para un usuario específico."""
    form = BotIntegrationForm()
    tree = tree_node_service.get_tree_nodes_by_user(current_user.id)
    tree = tree[0].to_dict() if tree else []

    return render_template('botintegration/index.html', tree=tree, form=form)


@botintegration_bp.route('/botintegration/add-bot', methods=['GET', 'POST'])
@login_required
def create_node_route_add_bot():
    """Agrega un nuevo bot al árbol de nodos."""
    form = BotIntegrationForm()
    parent_id = form.parent_id.data
    name = form.name.data
    user_id = current_user.id
    single_child = False

    path = "TELEGRAM BOTS"
    if parent_id:
        parent = TreeNode.query.get(parent_id)
        if parent:
            path = f"{parent.path}/{name}"

    try:
        result = tree_node_service.create_node_route_add_bot(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )

        return tree_node_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='botintegration.index',
            success_msg='Bot created successfully!',
            error_template='botintegration/index.html',
            form=form
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear el bot: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))


@botintegration_bp.route('/botintegration/add-chat', methods=['GET', 'POST'])
@login_required
def create_node_route_add_chat():
    """Agrega un nuevo chat al árbol de nodos."""
    form = BotIntegrationForm()
    parent_id = form.parent_id.data
    name = form.name.data
    user_id = current_user.id
    single_child = False

    path = f"{user_id}/{name}"
    if parent_id:
        parent = TreeNode.query.get(parent_id)
        if parent:
            path = f"{parent.path}/{name}"

    try:
        result = tree_node_service.create_node_route_add_chat(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )

        return tree_node_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='botintegration.index',
            success_msg='Chat created successfully!',
            error_template='botintegration/index.html',
            form=form
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear el chat: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))


@botintegration_bp.route('/botintegration/add-types-notification', methods=['GET', 'POST'])
@login_required
def create_node_route_add_types_notification():
    """Agrega un nuevo tipo de notificación al árbol de nodos."""
    form = BotIntegrationForm()
    parent_id = form.parent_id.data
    name = form.name.data
    user_id = current_user.id
    single_child = True

    path = f"{user_id}/{name}"
    if parent_id:
        parent = TreeNode.query.get(parent_id)
        if parent:
            path = f"{parent.path}/{name}"

    try:
        result = tree_node_service.create_node_route_add_types_notification(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )

        return tree_node_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='botintegration.index',
            success_msg='Notification type added successfully!',
            error_template='botintegration/index.html',
            form=form
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error al agregar el tipo de notificación: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))


@botintegration_bp.route('/botintegration/add-feature', methods=['GET', 'POST'])
@login_required
def create_node_route_add_feature():
    """Agrega una nueva característica al árbol de nodos."""
    form = BotIntegrationForm()
    parent_id = form.parent_id.data
    name = form.name.data
    user_id = current_user.id
    single_child = False

    path = f"{user_id}/{name}"
    if parent_id:
        parent = TreeNode.query.get(parent_id)
        if parent:
            path = f"{parent.path}/{name}"

    try:
        result = tree_node_service.create_node_route_add_feature(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )

        return tree_node_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='botintegration.index',
            success_msg='Feature added successfully!',
            error_template='botintegration/index.html',
            form=form
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error al agregar la característica: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))


@botintegration_bp.route('/botintegration/delete/<int:node_id>', methods=['POST'])
@login_required
def delete_node(node_id):
    """Elimina un nodo específico y sus descendientes."""
    try:
        node = tree_node_service.get_or_404(node_id)
        if node.user_id != current_user.id:
            flash('You are not authorized to delete this node', 'error')
            return redirect(url_for('botintegration.index'))

        result = tree_node_service.delete_node(node_id)
        flash('Node deleted successfully!' if result else 'Error deleting node', 'success' if result else 'error')
        return redirect(url_for('botintegration.index'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))


@botintegration_bp.route('/botintegration/merge/<int:node_id>', methods=['POST'])
@login_required
def merge_node(node_id):
    """Elimina un nodo específico y sus descendientes."""
    try:
        node = tree_node_service.get_or_404(node_id)
        if node.user_id != current_user.id:
            flash('You are not authorized to delete this node', 'error')
            return redirect(url_for('botintegration.index'))

        result = tree_node_service.merge_node(node_id, current_user.id)
        flash('Node deleted successfully!' if result else 'Error deleting node', 'success' if result else 'error')
        return redirect(url_for('botintegration.index'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')
        return redirect(url_for('botintegration.index'))
