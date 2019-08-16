--
-- Name: biosamplealiquotfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplealiquotfact FROM PUBLIC;
REVOKE ALL ON TABLE biosamplealiquotfact FROM agrbrdf;
GRANT ALL ON TABLE biosamplealiquotfact TO agrbrdf;
GRANT SELECT ON TABLE biosamplealiquotfact TO gbs;


