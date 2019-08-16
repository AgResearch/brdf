--
-- Name: microarrayspotfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE microarrayspotfact FROM PUBLIC;
REVOKE ALL ON TABLE microarrayspotfact FROM agrbrdf;
GRANT ALL ON TABLE microarrayspotfact TO agrbrdf;
GRANT SELECT ON TABLE microarrayspotfact TO gbs;


