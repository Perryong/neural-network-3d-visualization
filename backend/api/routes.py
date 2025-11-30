"""API route handlers for Neural Network Visualization backend."""

from flask import Blueprint, jsonify, request

from backend.api.models import ApiResponse
from backend.services import asset_service, training_service

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify(ApiResponse(
        success=True,
        message="API is healthy"
    ).to_dict())


@api_bp.route('/model/info', methods=['GET'])
def get_model_info():
    """Get model metadata and weights information."""
    try:
        info = training_service.get_model_info()
        return jsonify(ApiResponse(
            success=True,
            data=info
        ).to_dict())
    except Exception as e:
        return jsonify(ApiResponse(
            success=False,
            message=f"Error getting model info: {e}"
        ).to_dict()), 500


@api_bp.route('/training/start', methods=['POST'])
def start_training():
    """Start training job with optional hyperparameters."""
    try:
        data = request.get_json() or {}
        force = data.get('force', False)
        skip_if_exists = not force
        
        # Extract hyperparameters
        hyperparameters = {
            'epochs': data.get('epochs'),
            'batch_size': data.get('batch_size'),
            'hidden_dims': data.get('hidden_dims'),
            'lr': data.get('lr'),
            'device': data.get('device'),
        }
        
        # Remove None values
        hyperparameters = {k: v for k, v in hyperparameters.items() if v is not None}
        
        result = training_service.run_training(
            skip_if_exists=skip_if_exists,
            force=force,
            **hyperparameters
        )
        
        if result.get('success'):
            return jsonify(ApiResponse(
                success=True,
                data=result,
                message=result.get('message', 'Training completed')
            ).to_dict())
        else:
            # Include more detailed error information
            error_message = result.get('error', 'Training failed')
            if result.get('stderr'):
                error_message += f"\n\nStderr: {result.get('stderr')}"
            if result.get('stdout'):
                error_message += f"\n\nStdout: {result.get('stdout')}"
            return jsonify(ApiResponse(
                success=False,
                data=result,
                message=error_message
            ).to_dict()), 500
    except Exception as e:
        return jsonify(ApiResponse(
            success=False,
            message=f"Error starting training: {e}"
        ).to_dict()), 500


@api_bp.route('/training/status', methods=['GET'])
def training_status():
    """Get training status."""
    try:
        weights_exist = training_service.check_weights_exist()
        model_info = training_service.get_model_info()
        
        return jsonify(ApiResponse(
            success=True,
            data={
                "weights_exist": weights_exist,
                "model_info": model_info
            }
        ).to_dict())
    except Exception as e:
        return jsonify(ApiResponse(
            success=False,
            message=f"Error getting training status: {e}"
        ).to_dict()), 500


@api_bp.route('/training/progress', methods=['GET'])
def training_progress():
    """Get current training progress."""
    try:
        progress = training_service.get_training_progress()
        return jsonify(ApiResponse(
            success=True,
            data=progress
        ).to_dict())
    except Exception as e:
        return jsonify(ApiResponse(
            success=False,
            message=f"Error getting training progress: {e}"
        ).to_dict()), 500


@api_bp.route('/assets/prepare-mnist', methods=['POST'])
def prepare_mnist():
    """Prepare MNIST test assets."""
    try:
        data = request.get_json() or {}
        force = data.get('force', False)
        skip_if_exists = not force
        
        result = asset_service.prepare_mnist_assets(
            skip_if_exists=skip_if_exists,
            force=force
        )
        
        if result.get('success'):
            return jsonify(ApiResponse(
                success=True,
                data=result,
                message=result.get('message', 'MNIST assets prepared')
            ).to_dict())
        else:
            return jsonify(ApiResponse(
                success=False,
                data=result,
                message=result.get('error', 'MNIST preparation failed')
            ).to_dict()), 500
    except Exception as e:
        return jsonify(ApiResponse(
            success=False,
            message=f"Error preparing MNIST assets: {e}"
        ).to_dict()), 500


@api_bp.route('/assets/mnist-status', methods=['GET'])
def mnist_status():
    """Get MNIST asset status."""
    try:
        status = asset_service.get_mnist_status()
        return jsonify(ApiResponse(
            success=True,
            data=status
        ).to_dict())
    except Exception as e:
        return jsonify(ApiResponse(
            success=False,
            message=f"Error getting MNIST status: {e}"
        ).to_dict()), 500


@api_bp.route('/timeline/validate', methods=['GET'])
def validate_timeline():
    """Validate timeline entries."""
    try:
        fix = request.args.get('fix', 'false').lower() == 'true'
        result = training_service.validate_timeline(fix=fix)
        
        return jsonify(ApiResponse(
            success=True,
            data=result
        ).to_dict())
    except Exception as e:
        return jsonify(ApiResponse(
            success=False,
            message=f"Error validating timeline: {e}"
        ).to_dict()), 500


@api_bp.route('/timeline/fix', methods=['POST'])
def fix_timeline():
    """Fix timeline issues by removing invalid entries."""
    try:
        result = training_service.validate_timeline(fix=True)
        
        return jsonify(ApiResponse(
            success=True,
            data=result,
            message=result.get('message', 'Timeline fixed')
        ).to_dict())
    except Exception as e:
        return jsonify(ApiResponse(
            success=False,
            message=f"Error fixing timeline: {e}"
        ).to_dict()), 500

