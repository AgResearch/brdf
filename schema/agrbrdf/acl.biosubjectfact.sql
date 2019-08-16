--
-- Name: biosubjectfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosubjectfact FROM PUBLIC;
REVOKE ALL ON TABLE biosubjectfact FROM agrbrdf;
GRANT ALL ON TABLE biosubjectfact TO agrbrdf;
GRANT SELECT ON TABLE biosubjectfact TO gbs;


