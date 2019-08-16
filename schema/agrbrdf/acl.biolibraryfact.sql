--
-- Name: biolibraryfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biolibraryfact FROM PUBLIC;
REVOKE ALL ON TABLE biolibraryfact FROM agrbrdf;
GRANT ALL ON TABLE biolibraryfact TO agrbrdf;
GRANT SELECT ON TABLE biolibraryfact TO gbs;


