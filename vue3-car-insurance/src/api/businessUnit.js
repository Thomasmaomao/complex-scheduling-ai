/**
 * 业务单元管理 API
 * 后端路由：/api/v1/business-unit/*
 */
import api from './request'

/**
 * 获取所有业务单元列表
 */
export function getAllBusinessUnits() {
  return api.get('/business-unit/list')
}

/**
 * 获取单个业务单元详情
 * @param {string} unitId - 业务单元 ID
 */
export function getBusinessUnit(unitId) {
  return api.get(`/business-unit/${unitId}`)
}
