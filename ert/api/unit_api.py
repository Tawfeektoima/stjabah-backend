"""API handlers for ERT unit endpoints"""

from flask import Blueprint, request, jsonify
import logging

from ert.service.unit_service import UnitService

logger = logging.getLogger(__name__)

ert_bp = Blueprint('ert', __name__)

def init_ert_api(unit_service: UnitService):
    """Initialize the ERT API with service dependencies"""
    ert_bp.unit_service = unit_service
    return ert_bp


